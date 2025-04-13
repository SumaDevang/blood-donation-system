import csv
from flask import Flask, render_template, request, redirect, url_for, g, Response
import sqlite3
from collections import defaultdict

# Initialize the Flask app
app = Flask(__name__)

# Database configuration
DATABASE = 'database.db'


# Database connection helper functions
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, timeout=10)
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
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # Handle Donor Registration Form
        if form_type == 'register':
            conn = get_db()
            name = request.form['name']
            dob = request.form['dob']
            blood_type = request.form['blood_type']
            contact = request.form['contact']
            email = request.form['email']
            last_donation = request.form.get('last_donation')
            try:
                conn.execute('INSERT INTO Donors (Name, DateOfBirth, BloodType, ContactInfo, Email, LastDonationDate) VALUES (?, ?, ?, ?, ?, ?)',
                             (name, dob, blood_type, contact, email, last_donation))
                conn.commit()
                return render_template('donate_blood.html', active_page='donate_blood',
                                      success="Donor registered successfully! Please use the Donor Dashboard to schedule donations.")
            except sqlite3.OperationalError as e:
                return render_template('donate_blood.html', active_page='donate_blood',
                                      error=f"Database error: {e}"), 500

    return render_template('donate_blood.html', active_page='donate_blood')


# Donor Dashboard
@app.route('/donor', methods=['GET', 'POST'])
def donor_dashboard():
    conn = get_db()
    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()
    donor = None
    donation_history = None
    upcoming_appointments = None

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # Handle Donor Lookup
        if form_type == 'lookup':
            donor_email = request.form['donor_email']
            donor = conn.execute('SELECT * FROM Donors WHERE Email = ?', (donor_email,)).fetchone()
            if donor:
                donor_id = donor['DonorID']
                donation_history = conn.execute('''
                    SELECT Donations.*, Hospitals.Name AS HospitalName
                    FROM Donations
                    JOIN Hospitals ON Donations.HospitalID = Hospitals.HospitalID
                    WHERE Donations.DonorID = ?
                ''', (donor_id,)).fetchall()
                upcoming_appointments = conn.execute('''
                    SELECT Donations.*, Hospitals.Name AS HospitalName
                    FROM Donations
                    JOIN Hospitals ON Donations.HospitalID = Hospitals.HospitalID
                    WHERE Donations.DonorID = ? AND Donations.Status = 'Scheduled'
                ''', (donor_id,)).fetchall()
            else:
                return render_template('donor_dashboard.html', hospitals=hospitals,
                                      error="Donor not found. Please register on the Donate Blood page.")

        # Handle Donation Scheduling
        elif form_type == 'schedule':
            donor_email = request.form['donor_email']
            hospital_id = request.form['hospital_id']
            donation_date = request.form['donation_date']

            donor = conn.execute('SELECT * FROM Donors WHERE Email = ?', (donor_email,)).fetchone()
            if not donor:
                return render_template('donor_dashboard.html', hospitals=hospitals,
                                      error="Donor not found. Please register on the Donate Blood page."), 400

            blood_type = donor['BloodType']
            donor_id = donor['DonorID']

            try:
                conn.execute('INSERT INTO Donations (DonorID, HospitalID, DonationDate, BloodType, Status) VALUES (?, ?, ?, ?, ?)',
                             (donor_id, hospital_id, donation_date, blood_type, 'Scheduled'))
                conn.commit()

                # Refresh donor data after scheduling
                donor = conn.execute('SELECT * FROM Donors WHERE Email = ?', (donor_email,)).fetchone()
                donation_history = conn.execute('''
                    SELECT Donations.*, Hospitals.Name AS HospitalName
                    FROM Donations
                    JOIN Hospitals ON Donations.HospitalID = Hospitals.HospitalID
                    WHERE Donations.DonorID = ?
                ''', (donor_id,)).fetchall()
                upcoming_appointments = conn.execute('''
                    SELECT Donations.*, Hospitals.Name AS HospitalName
                    FROM Donations
                    JOIN Hospitals ON Donations.HospitalID = Hospitals.HospitalID
                    WHERE Donations.DonorID = ? AND Donations.Status = 'Scheduled'
                ''', (donor_id,)).fetchall()

                return render_template('donor_dashboard.html', hospitals=hospitals, donor=donor,
                                      donation_history=donation_history, upcoming_appointments=upcoming_appointments,
                                      success=f"Donation scheduled for {donation_date}!")
            except sqlite3.OperationalError as e:
                return render_template('donor_dashboard.html', hospitals=hospitals, donor=donor,
                                      donation_history=donation_history, upcoming_appointments=upcoming_appointments,
                                      error=f"Database error: {e}"), 500

    return render_template('donor_dashboard.html', hospitals=hospitals, donor=donor,
                          donation_history=donation_history, upcoming_appointments=upcoming_appointments)

# Cancel Appointment
@app.route('/donor/cancel/<int:donation_id>')
def cancel_appointment(donation_id):
    conn = get_db()
    try:
        # Ensure only scheduled donations can be canceled
        conn.execute("DELETE FROM Donations WHERE DonationID = ? AND Status = 'Scheduled'", (donation_id,))
        conn.commit()
    except sqlite3.OperationalError as e:
        return render_template('donor_dashboard.html', hospitals=conn.execute('SELECT * FROM Hospitals').fetchall(),
                              error=f"Database error: {e}"), 500
    return redirect(url_for('donor_dashboard'))

# Hospital Dashboard
@app.route('/hospital', methods=['GET', 'POST'])
def hospital_dashboard():
    conn = get_db()
    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()
    selected_hospital = None
    blood_requests = None
    scheduled_donations = None
    donors_by_blood_type = None
    blood_type_searched = None
    success = None
    error = None

    # Check if hospital_id is passed as a query parameter (for redirects)
    hospital_id = request.args.get('hospital_id') or request.form.get('hospital_id')
    if hospital_id:
        selected_hospital = conn.execute('SELECT * FROM Hospitals WHERE HospitalID = ?', (hospital_id,)).fetchone()
        if selected_hospital:
            # Fetch blood requests for the selected hospital
            blood_requests = conn.execute('SELECT * FROM BloodRequests WHERE HospitalID = ?', (hospital_id,)).fetchall()

            # Fetch scheduled donations for the selected hospital
            scheduled_donations = conn.execute('''
                SELECT Donations.*, Donors.Name AS DonorName
                FROM Donations
                JOIN Donors ON Donations.DonorID = Donors.DonorID
                WHERE Donations.HospitalID = ? AND Donations.Status = 'Scheduled'
            ''', (hospital_id,)).fetchall()

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # Handle Blood Request Form
        if form_type == 'request':
            hospital_id = request.form['hospital_id']
            blood_type = request.form['blood_type']
            quantity = request.form['quantity']
            request_date = request.form['request_date']
            try:
                conn.execute('INSERT INTO BloodRequests (HospitalID, BloodType, Quantity, RequestDate) VALUES (?, ?, ?, ?)',
                             (hospital_id, blood_type, quantity, request_date))
                conn.commit()
                # Redirect with hospital_id to refresh the page with updated data
                return redirect(url_for('hospital_dashboard', hospital_id=hospital_id, success="Blood request added successfully!"))
            except sqlite3.OperationalError as e:
                return render_template('hospital_dashboard.html', hospitals=hospitals, selected_hospital=selected_hospital,
                                      blood_requests=blood_requests, scheduled_donations=scheduled_donations,
                                      error=f"Database error: {e}"), 500

        # Handle Donor Search by Blood Type
        elif form_type == 'search_donors':
            hospital_id = request.form['hospital_id']
            blood_type_searched = request.form['blood_type']
            donors_by_blood_type = conn.execute('SELECT * FROM Donors WHERE BloodType = ?', (blood_type_searched,)).fetchall()
            # Re-render with the selected hospital data
            return render_template('hospital_dashboard.html', hospitals=hospitals, selected_hospital=selected_hospital,
                                  blood_requests=blood_requests, scheduled_donations=scheduled_donations,
                                  donors_by_blood_type=donors_by_blood_type, blood_type_searched=blood_type_searched)

    # Get success message from query parameter (if any)
    success = request.args.get('success')
    error = request.args.get('error')

    return render_template('hospital_dashboard.html', hospitals=hospitals, selected_hospital=selected_hospital,
                          blood_requests=blood_requests, scheduled_donations=scheduled_donations,
                          donors_by_blood_type=donors_by_blood_type, blood_type_searched=blood_type_searched,
                          success=success, error=error)

# Delete Blood Request
@app.route('/hospital/delete-request/<int:request_id>')
def delete_blood_request(request_id):
    conn = get_db()
    # Get the hospital_id of the request to redirect back to the same hospital
    request = conn.execute('SELECT HospitalID FROM BloodRequests WHERE RequestID = ?', (request_id,)).fetchone()
    if not request:
        return "Blood request not found.", 404
    hospital_id = request['HospitalID']
    try:
        conn.execute('DELETE FROM BloodRequests WHERE RequestID = ?', (request_id,))
        conn.commit()
    except sqlite3.OperationalError as e:
        return redirect(url_for('hospital_dashboard', hospital_id=hospital_id, error=f"Database error: {e}"))
    return redirect(url_for('hospital_dashboard', hospital_id=hospital_id, success="Blood request deleted successfully!"))

# Admin Dashboard
@app.route('/admin')
def admin_dashboard():
    conn = get_db()
    donors = conn.execute('SELECT * FROM Donors').fetchall()
    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()
    donations = conn.execute('SELECT * FROM Donations').fetchall()
    blood_requests = conn.execute('SELECT * FROM BloodRequests').fetchall()

    # System Summary
    summary = {
        'total_donors': len(donors),
        'total_hospitals': len(hospitals),
        'total_donations': len(donations),
        'total_blood_requests': len(blood_requests)
    }

    # Donors by Blood Type
    donors_by_blood_type = defaultdict(int)
    for donor in donors:
        donors_by_blood_type[donor['BloodType']] += 1

    # Donations per Hospital
    donations_per_hospital = conn.execute('''
        SELECT Hospitals.Name, COUNT(Donations.DonationID) as DonationCount
        FROM Hospitals
        LEFT JOIN Donations ON Hospitals.HospitalID = Donations.HospitalID
        GROUP BY Hospitals.HospitalID, Hospitals.Name
    ''').fetchall()

    return render_template('admin_dashboard.html', donors=donors, hospitals=hospitals,
                          donations=donations, blood_requests=blood_requests,
                          summary=summary, donors_by_blood_type=donors_by_blood_type,
                          donations_per_hospital=donations_per_hospital)


# Add Hospital
@app.route('/hospital/add', methods=['GET', 'POST'])
def add_hospital():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        contact_info = request.form['contact_info']
        hospital_type = request.form['hospital_type']
        conn = get_db()
        try:
            conn.execute('INSERT INTO Hospitals (Name, Location, ContactInfo, HospitalType) VALUES (?, ?, ?, ?)',
                         (name, location, contact_info, hospital_type))
            conn.commit()
        except sqlite3.OperationalError as e:
            return f"Database error: {e}", 500
        return redirect(url_for('admin_dashboard'))
    return render_template('add_hospital.html')

# Edit Hospital
@app.route('/hospital/edit/<int:id>', methods=['GET', 'POST'])
def edit_hospital(id):
    conn = get_db()
    hospital = conn.execute('SELECT * FROM Hospitals WHERE HospitalID = ?', (id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        contact_info = request.form['contact_info']
        hospital_type = request.form['hospital_type']
        try:
            conn.execute('UPDATE Hospitals SET Name = ?, Location = ?, ContactInfo = ?, HospitalType = ? WHERE HospitalID = ?',
                         (name, location, contact_info, hospital_type, id))
            conn.commit()
        except sqlite3.OperationalError as e:
            return f"Database error: {e}", 500
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_hospital.html', hospital=hospital)

# Delete Hospital
@app.route('/hospital/delete/<int:id>')
def delete_hospital(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM Hospitals WHERE HospitalID = ?', (id,))
        conn.commit()
    except sqlite3.OperationalError as e:
        return f"Database error: {e}", 500
    return redirect(url_for('admin_dashboard'))


# Edit Donation
@app.route('/donation/edit/<int:id>', methods=['GET', 'POST'])
def edit_donation(id):
    conn = get_db()
    donation = conn.execute('SELECT * FROM Donations WHERE DonationID = ?', (id,)).fetchone()
    if request.method == 'POST':
        donor_id = request.form['donor_id']
        hospital_id = request.form['hospital_id']
        donation_date = request.form['donation_date']
        blood_type = request.form['blood_type']
        status = request.form['status']
        try:
            conn.execute('UPDATE Donations SET DonorID = ?, HospitalID = ?, DonationDate = ?, BloodType = ?, Status = ? WHERE DonationID = ?',
                         (donor_id, hospital_id, donation_date, blood_type, status, id))
            conn.commit()
        except sqlite3.OperationalError as e:
            return f"Database error: {e}", 500
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_donation.html', donation=donation)

# Delete Donation
@app.route('/donation/delete/<int:id>')
def delete_donation(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM Donations WHERE DonationID = ?', (id,))
        conn.commit()
    except sqlite3.OperationalError as e:
        return f"Database error: {e}", 500
    return redirect(url_for('admin_dashboard'))


# Edit Blood Request
@app.route('/blood-request/edit/<int:id>', methods=['GET', 'POST'])
def edit_blood_request(id):
    conn = get_db()
    request_data = conn.execute('SELECT * FROM BloodRequests WHERE RequestID = ?', (id,)).fetchone()
    if request.method == 'POST':
        hospital_id = request.form['hospital_id']
        blood_type = request.form['blood_type']
        quantity = request.form['quantity']
        request_date = request.form['request_date']
        try:
            conn.execute(
                'UPDATE BloodRequests SET HospitalID = ?, BloodType = ?, Quantity = ?, RequestDate = ? WHERE RequestID = ?',
                (hospital_id, blood_type, quantity, request_date, id))
            conn.commit()
        except sqlite3.OperationalError as e:
            return f"Database error: {e}", 500
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_blood_request.html', request=request_data)


# Download Donations Report
@app.route('/download-donations-report')
def download_donations_report():
    conn = get_db()
    donations = conn.execute('SELECT * FROM Donations').fetchall()

    # Create CSV content
    output = []
    output.append(','.join(['DonationID', 'DonorID', 'HospitalID', 'DonationDate', 'BloodType', 'Status']))
    for donation in donations:
        output.append(','.join([str(donation['DonationID']), str(donation['DonorID']),
                                str(donation['HospitalID']), donation['DonationDate'],
                                donation['BloodType'], donation['Status']]))

    # Return CSV as a downloadable file
    return Response(
        '\n'.join(output),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=donations_report.csv'}
    )

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
        return redirect(url_for('admin_dashboard'))
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
    return redirect(url_for('admin_dashboard'))


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


# Predefined Query: Donors by Blood Type
@app.route('/donors_by_blood_type')
def donors_by_blood_type():
    conn = get_db()
    query = '''
    SELECT BloodType, COUNT(*) as Count
    FROM Donors
    GROUP BY BloodType
    '''
    results = conn.execute(query).fetchall()
    return render_template('query_results.html', results=results, title="Donors by Blood Type")

# Predefined Query: Recent Donations (Last 5 Completed)
@app.route('/recent_donations')
def recent_donations():
    conn = get_db()
    query = '''
    SELECT Donors.Name, Hospitals.Name AS HospitalName, Donations.DonationDate, Donations.BloodType
    FROM Donations
    JOIN Donors ON Donations.DonorID = Donors.DonorID
    JOIN Hospitals ON Donations.HospitalID = Hospitals.HospitalID
    WHERE Donations.Status = 'Completed'
    ORDER BY Donations.DonationDate DESC
    LIMIT 5
    '''
    results = conn.execute(query).fetchall()
    return render_template('query_results.html', results=results, title="Recent Donations (Last 5 Completed)")

# Predefined Query: Hospitals with Most Donations (Top 3)
@app.route('/hospitals_with_most_donations')
def hospitals_with_most_donations():
    conn = get_db()
    query = '''
    SELECT Hospitals.Name, COUNT(Donations.DonationID) as DonationCount
    FROM Hospitals
    LEFT JOIN Donations ON Hospitals.HospitalID = Donations.HospitalID
    GROUP BY Hospitals.HospitalID, Hospitals.Name
    ORDER BY DonationCount DESC
    LIMIT 3
    '''
    results = conn.execute(query).fetchall()
    return render_template('query_results.html', results=results, title="Hospitals with Most Donations (Top 3)")

# Biomedical Services page
@app.route('/biomedical-services')
def biomedical_services():
    conn = get_db()
    total_donations = conn.execute('SELECT COUNT(*) FROM Donations').fetchone()[0]
    total_units_available = conn.execute("SELECT COUNT(*) FROM Donations WHERE Status = 'Completed'").fetchone()[0]
    stats = {
        'total_donations': total_donations,
        'total_units_available': total_units_available
    }
    return render_template('biomedical_services.html', active_page='biomedical_services', stats=stats)


if __name__ == '__main__':
    app.run(debug=True, port=5002)