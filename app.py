from flask import Flask, render_template, request, redirect, url_for
import sqlite3

# Initialize the Flask app
app = Flask(__name__)

# Database connection helper function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Homepage
@app.route('/')
def index():
    return render_template('index.html', active_page='index')

# Donate Blood page
@app.route('/donate-blood')
def donate_blood():
    return render_template('donate_blood.html', active_page='donate_blood')

# Host a Blood Drive page
@app.route('/host-blood-drive')
def host_blood_drive():
    return render_template('host_blood_drive.html', active_page='host_blood_drive')

# Biomedical Services page
@app.route('/biomedical-services')
def biomedical_services():
    return render_template('biomedical_services.html', active_page='biomedical_services')

# Donor Dashboard
@app.route('/donor')
def donor_dashboard():
    conn = get_db_connection()
    donors = conn.execute('SELECT * FROM Donors').fetchall()
    conn.close()
    return render_template('donor_dashboard.html', donors=donors)

# Hospital Dashboard
@app.route('/hospital')
def hospital_dashboard():
    conn = get_db_connection()
    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()
    conn.close()
    return render_template('hospital_dashboard.html', hospitals=hospitals)

# Admin Dashboard
@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    donations = conn.execute('SELECT * FROM Donations').fetchall()
    conn.close()
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
        conn = get_db_connection()
        conn.execute('INSERT INTO Donors (Name, DateOfBirth, BloodType, ContactInfo, Email, LastDonationDate) VALUES (?, ?, ?, ?, ?, ?)',
                     (name, dob, blood_type, contact, email, last_donation))
        conn.commit()
        conn.close()
        return redirect(url_for('donor_dashboard'))
    return render_template('add_donor.html')

# CRUD: Update Donor
@app.route('/donor/edit/<int:id>', methods=['GET', 'POST'])
def edit_donor(id):
    conn = get_db_connection()
    donor = conn.execute('SELECT * FROM Donors WHERE DonorID = ?', (id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        blood_type = request.form['blood_type']
        contact = request.form['contact']
        email = request.form['email']
        last_donation = request.form['last_donation'] or None
        conn.execute('UPDATE Donors SET Name = ?, DateOfBirth = ?, BloodType = ?, ContactInfo = ?, Email = ?, LastDonationDate = ? WHERE DonorID = ?',
                     (name, dob, blood_type, contact, email, last_donation, id))
        conn.commit()
        conn.close()
        return redirect(url_for('donor_dashboard'))
    conn.close()
    return render_template('edit_donor.html', donor=donor)

# CRUD: Delete Donor
@app.route('/donor/delete/<int:id>')
def delete_donor(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Donors WHERE DonorID = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('donor_dashboard'))

# Predefined Query: Scheduled Donations
@app.route('/scheduled_donations')
def scheduled_donations():
    conn = get_db_connection()
    query = '''
    SELECT Donors.Name, Hospitals.Name AS HospitalName, Donations.DonationDate, Donations.Status
    FROM Donations
    JOIN Donors ON Donations.DonorID = Donors.DonorID
    JOIN Hospitals ON Donations.HospitalID = Hospitals.HospitalID
    WHERE Donations.Status = 'Scheduled'
    '''
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template('query_results.html', results=results, title="Scheduled Donations")

# Predefined Query: Eligible Donors
@app.route('/eligible_donors')
def eligible_donors():
    conn = get_db_connection()
    query = '''
    SELECT Donors.Name, DonationEligibility.EligibilityStatus
    FROM Donors
    JOIN DonationEligibility ON Donors.DonorID = DonationEligibility.DonorID
    WHERE DonationEligibility.EligibilityStatus = 'Eligible'
    '''
    results = conn.execute(query).fetchall()
    conn.close()
    return render_template('query_results.html', results=results, title="Eligible Donors")

if __name__ == '__main__':
    app.run(debug=True, port=5001)