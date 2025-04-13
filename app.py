from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

# Initialize the Flask app
app = Flask(__name__)

# Database configuration
DATABASE = 'database.db'


# Database connection helper functions
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, timeout=10)  # Set timeout to 10 seconds
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Homepage
@app.route('/')
def index():
    return render_template('index.html', active_page='index')


# Donate Blood page
@app.route('/donate-blood', methods=['GET', 'POST'])
def donate_blood():
    conn = get_db()

    # Fetch hospitals for the scheduling form
    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # Handle Donor Registration Form
        if form_type == 'register':
            name = request.form['name']
            dob = request.form['dob']
            blood_type = request.form['blood_type']
            contact = request.form['contact']
            email = request.form['email']
            last_donation = request.form['last_donation'] or None
            try:
                conn.execute(
                    'INSERT INTO Donors (Name, DateOfBirth, BloodType, ContactInfo, Email, LastDonationDate) VALUES (?, ?, ?, ?, ?, ?)',
                    (name, dob, blood_type, contact, email, last_donation))
                conn.commit()
            except sqlite3.OperationalError as e:
                return f"Database error: {e}", 500

        # Handle Donation Scheduling Form
        elif form_type == 'schedule':
            donor_email = request.form['donor_email']
            hospital_id = request.form['hospital_id']
            donation_date = request.form['donation_date']

            # Find the donor by email
            donor = conn.execute('SELECT * FROM Donors WHERE Email = ?', (donor_email,)).fetchone()
            if not donor:
                return "Error: Donor not found. Please register first.", 400

            # Get the donor's blood type
            blood_type = donor['BloodType']
            donor_id = donor['DonorID']

            # Insert the donation record
            try:
                conn.execute(
                    'INSERT INTO Donations (DonorID, HospitalID, DonationDate, BloodType, Status) VALUES (?, ?, ?, ?, ?)',
                    (donor_id, hospital_id, donation_date, blood_type, 'Scheduled'))
                conn.commit()
            except sqlite3.OperationalError as e:
                return f"Database error: {e}", 500

        return redirect(url_for('donate_blood'))  # Redirect to refresh the page

    return render_template('donate_blood.html', active_page='donate_blood', hospitals=hospitals)


# Donor Dashboard
@app.route('/donor')
def donor_dashboard():
    conn = get_db()
    donors = conn.execute('SELECT * FROM Donors').fetchall()
    return render_template('donor_dashboard.html', donors=donors)


# Hospital Dashboard
@app.route('/hospital')
def hospital_dashboard():
    conn = get_db()
    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()
    return render_template('hospital_dashboard.html', hospitals=hospitals)


# Admin Dashboard
@app.route('/admin')
def admin_dashboard():
    conn = get_db()
    donations = conn.execute('SELECT * FROM Donations').fetchall()
    return render_template('admin_dashboard.html', donations=donations)


# CRUD: Create Donor
@app.route('/donor/add', methods=['GET', 'POST'])
def add_donor():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        blood_type = request.form['blood_type']
        contact = request.form['contact']
        email = request.form['email']
        last_donation = request.form['last_donation'] or None
        conn = get_db()
        try:
            conn.execute(
                'INSERT INTO Donors (Name, DateOfBirth, BloodType, ContactInfo, Email, LastDonationDate) VALUES (?, ?, ?, ?, ?, ?)',
                (name, dob, blood_type, contact, email, last_donation))
            conn.commit()
        except sqlite3.OperationalError as e:
            return f"Database error: {e}", 500
        return redirect(url_for('donor_dashboard'))
    return render_template('add_donor.html')


# CRUD: Update Donor
@app.route('/donor/edit/<int:id>', methods=['GET', 'POST'])
def edit_donor(id):
    conn = get_db()
    donor = conn.execute('SELECT * FROM Donors WHERE DonorID = ?', (id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        blood_type = request.form['blood_type']
        contact = request.form['contact']
        email = request.form['email']
        last_donation = request.form['last_donation'] or None
        try:
            conn.execute(
                'UPDATE Donors SET Name = ?, DateOfBirth = ?, BloodType = ?, ContactInfo = ?, Email = ?, LastDonationDate = ? WHERE DonorID = ?',
                (name, dob, blood_type, contact, email, last_donation, id))
            conn.commit()
        except sqlite3.OperationalError as e:
            return f"Database error: {e}", 500
        return redirect(url_for('donor_dashboard'))
    return render_template('edit_donor.html', donor=donor)


# CRUD: Delete Donor
@app.route('/donor/delete/<int:id>')
def delete_donor(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM Donors WHERE DonorID = ?', (id,))
        conn.commit()
    except sqlite3.OperationalError as e:
        return f"Database error: {e}", 500
    return redirect(url_for('donor_dashboard'))


# Predefined Query: Scheduled Donations
@app.route('/scheduled_donations')
def scheduled_donations():
    conn = get_db()
    query = '''
    SELECT Donors.Name, Hospitals.Name AS HospitalName, Donations.DonationDate, Donations.Status
    FROM Donations
    JOIN Donors ON Donations.DonorID = Donors.DonorID
    JOIN Hospitals ON Donations.HospitalID = Hospitals.HospitalID
    WHERE Donations.Status = 'Scheduled'
    '''
    results = conn.execute(query).fetchall()
    return render_template('query_results.html', results=results, title="Scheduled Donations")


# Predefined Query: Eligible Donors
@app.route('/eligible_donors')
def eligible_donors():
    conn = get_db()
    query = '''
    SELECT Donors.Name, DonationEligibility.EligibilityStatus
    FROM Donors
    JOIN DonationEligibility ON Donors.DonorID = DonationEligibility.DonorID
    WHERE DonationEligibility.EligibilityStatus = 'Eligible'
    '''
    results = conn.execute(query).fetchall()
    return render_template('query_results.html', results=results, title="Eligible Donors")


# Host a Blood Drive page
@app.route('/host-blood-drive')
def host_blood_drive():
    return render_template('host_blood_drive.html', active_page='host_blood_drive')


# Biomedical Services page
@app.route('/biomedical-services')
def biomedical_services():
    return render_template('biomedical_services.html', active_page='biomedical_services')


if __name__ == '__main__':
    app.run(debug=True, port=5001)