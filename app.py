from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from collections import defaultdict

app = Flask(__name__)


# Database connection helper
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Homepage
@app.route('/')
def index():
    return render_template('index.html', active_page='index')


# Donor Registration page
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
                conn.execute(
                    'INSERT INTO Donors (Name, DateOfBirth, BloodType, ContactInfo, Email, LastDonationDate) VALUES (?, ?, ?, ?, ?, ?)',
                    (name, dob, blood_type, contact, email, last_donation))
                conn.commit()
                return render_template('donate_blood.html', active_page='donate_blood',
                                       success="Donor registered successfully! Please use the Donor Dashboard to manage your donations.")
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
                                       error="Donor not found. Please register on the Donor Registration page.")

        # Handle Donation Scheduling
        elif form_type == 'schedule':
            donor_email = request.form['donor_email']
            hospital_id = request.form['hospital_id']
            donation_date = request.form['donation_date']

            donor = conn.execute('SELECT * FROM Donors WHERE Email = ?', (donor_email,)).fetchone()
            if not donor:
                return render_template('donor_dashboard.html', hospitals=hospitals,
                                       error="Donor not found. Please register on the Donor Registration page."), 400

            blood_type = donor['BloodType']
            donor_id = donor['DonorID']

            try:
                conn.execute(
                    'INSERT INTO Donations (DonorID, HospitalID, DonationDate, BloodType, Status) VALUES (?, ?, ?, ?, ?)',
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
    return redirect(url_for('donor_dashboard', success="Appointment canceled successfully!"))


# Hospital Dashboard
@app.route('/hospital')
def hospital_dashboard():
    conn = get_db()
    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()
    blood_requests = conn.execute('SELECT * FROM BloodRequests').fetchall()
    donations = conn.execute('''
        SELECT Donations.*, Donors.Name AS DonorName, Hospitals.Name AS HospitalName
        FROM Donations
        JOIN Donors ON Donations.DonorID = Donors.DonorID
        JOIN Hospitals ON Donations.HospitalID = Hospitals.HospitalID
    ''').fetchall()
    return render_template('hospital_dashboard.html', hospitals=hospitals, blood_requests=blood_requests,
                           donations=donations)


# Request Blood
@app.route('/hospital/request-blood', methods=['GET', 'POST'])
def request_blood():
    conn = get_db()
    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()
    if request.method == 'POST':
        hospital_id = request.form['hospital_id']
        blood_type = request.form['blood_type']
        quantity = request.form['quantity']
        request_date = request.form['request_date']
        try:
            conn.execute('INSERT INTO BloodRequests (HospitalID, BloodType, Quantity, RequestDate) VALUES (?, ?, ?, ?)',
                         (hospital_id, blood_type, quantity, request_date))
            conn.commit()
            return redirect(url_for('hospital_dashboard', success="Blood request submitted successfully!"))
        except sqlite3.OperationalError as e:
            return render_template('request_blood.html', hospitals=hospitals, error=f"Database error: {e}"), 500
    return render_template('request_blood.html', hospitals=hospitals)


# Admin Dashboard
@app.route('/admin')
def admin_dashboard():
    conn = get_db()
    donors = conn.execute('SELECT * FROM Donors').fetchall()
    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()
    blood_requests = conn.execute('SELECT * FROM BloodRequests').fetchall()
    donation_eligibility = conn.execute('SELECT * FROM DonationEligibility').fetchall()

    # Handle Status Filter for Donations
    status_filter = request.args.get('status_filter', 'all')
    if status_filter == 'all':
        donations = conn.execute('SELECT * FROM Donations').fetchall()
    else:
        donations = conn.execute('SELECT * FROM Donations WHERE Status = ?', (status_filter,)).fetchall()

    # System Summary
    summary = {
        'total_donors': len(donors),
        'total_hospitals': len(hospitals),
        'total_donations': conn.execute("SELECT COUNT(*) FROM Donations WHERE Status = 'Completed'").fetchone()[0],
        'total_blood_requests': len(blood_requests)
    }

    # Completed Donations by Blood Type (count of completed donations, not distinct donors)
    donors_by_blood_type = conn.execute('''
        SELECT Donors.BloodType, COUNT(Donations.DonationID) as Count
        FROM Donors
        JOIN Donations ON Donors.DonorID = Donations.DonorID
        WHERE Donations.Status = 'Completed'
        GROUP BY Donors.BloodType
    ''').fetchall()
    donors_by_blood_type = defaultdict(int, [(row['BloodType'], row['Count']) for row in donors_by_blood_type])

    # Donations per Hospital (only Completed donations)
    donations_per_hospital = conn.execute('''
        SELECT Hospitals.Name, COUNT(Donations.DonationID) as DonationCount
        FROM Hospitals
        LEFT JOIN Donations ON Hospitals.HospitalID = Donations.HospitalID AND Donations.Status = 'Completed'
        GROUP BY Hospitals.HospitalID, Hospitals.Name
    ''').fetchall()

    return render_template('admin_dashboard.html', donors=donors, hospitals=hospitals,
                          donations=donations, blood_requests=blood_requests,
                          donation_eligibility=donation_eligibility,
                          summary=summary, donors_by_blood_type=donors_by_blood_type,
                          donations_per_hospital=donations_per_hospital, status_filter=status_filter)


# Add New Donor
@app.route('/donor/add', methods=['GET', 'POST'])
def add_donor():
    if request.method == 'POST':
        conn = get_db()
        name = request.form['name']
        dob = request.form['dob']
        blood_type = request.form['blood_type']
        contact = request.form['contact']
        email = request.form['email']
        last_donation = request.form.get('last_donation')
        try:
            conn.execute(
                'INSERT INTO Donors (Name, DateOfBirth, BloodType, ContactInfo, Email, LastDonationDate) VALUES (?, ?, ?, ?, ?, ?)',
                (name, dob, blood_type, contact, email, last_donation))
            conn.commit()
            return redirect(url_for('admin_dashboard', success="Donor added successfully!"))
        except sqlite3.OperationalError as e:
            return render_template('add_donor.html', error=f"Database error: {e}"), 500
    return render_template('add_donor.html')


# Edit Donor
@app.route('/donor/edit/<int:id>', methods=['GET', 'POST'])
def edit_donor(id):
    conn = get_db()
    donor = conn.execute('SELECT * FROM Donors WHERE DonorID = ?', (id,)).fetchone()

    if not donor:
        return render_template('admin_dashboard.html', donors=conn.execute('SELECT * FROM Donors').fetchall(),
                               hospitals=conn.execute('SELECT * FROM Hospitals').fetchall(),
                               donations=conn.execute('SELECT * FROM Donations').fetchall(),
                               blood_requests=conn.execute('SELECT * FROM BloodRequests').fetchall(),
                               error="Donor not found."), 404

    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        blood_type = request.form['blood_type']
        contact = request.form['contact']
        email = request.form['email']
        last_donation = request.form.get('last_donation')
        try:
            conn.execute(
                'UPDATE Donors SET Name = ?, DateOfBirth = ?, BloodType = ?, ContactInfo = ?, Email = ?, LastDonationDate = ? WHERE DonorID = ?',
                (name, dob, blood_type, contact, email, last_donation, id))
            conn.commit()
        except sqlite3.OperationalError as e:
            return render_template('edit_donor.html', donor=donor, error=f"Database error: {e}"), 500
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_donor.html', donor=donor)


# Delete Donor
@app.route('/donor/delete/<int:id>')
def delete_donor(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM Donors WHERE DonorID = ?', (id,))
        conn.commit()
    except sqlite3.OperationalError as e:
        return f"Database error: {e}", 500
    return redirect(url_for('admin_dashboard'))


# Add New Hospital
@app.route('/hospital/add', methods=['GET', 'POST'])
def add_hospital():
    if request.method == 'POST':
        conn = get_db()
        name = request.form['name']
        location = request.form['location']
        contact = request.form['contact']
        hospital_type = request.form['hospital_type']
        try:
            conn.execute('INSERT INTO Hospitals (Name, Location, ContactInfo, HospitalType) VALUES (?, ?, ?, ?)',
                         (name, location, contact, hospital_type))
            conn.commit()
            return redirect(url_for('admin_dashboard', success="Hospital added successfully!"))
        except sqlite3.OperationalError as e:
            return render_template('add_hospital.html', error=f"Database error: {e}"), 500
    return render_template('add_hospital.html')


# Edit Hospital
@app.route('/hospital/edit/<int:id>', methods=['GET', 'POST'])
def edit_hospital(id):
    conn = get_db()
    hospital = conn.execute('SELECT * FROM Hospitals WHERE HospitalID = ?', (id,)).fetchone()

    if not hospital:
        return render_template('admin_dashboard.html', donors=conn.execute('SELECT * FROM Donors').fetchall(),
                               hospitals=conn.execute('SELECT * FROM Hospitals').fetchall(),
                               donations=conn.execute('SELECT * FROM Donations').fetchall(),
                               blood_requests=conn.execute('SELECT * FROM BloodRequests').fetchall(),
                               error="Hospital not found."), 404

    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        contact = request.form['contact']
        hospital_type = request.form['hospital_type']
        try:
            conn.execute(
                'UPDATE Hospitals SET Name = ?, Location = ?, ContactInfo = ?, HospitalType = ? WHERE HospitalID = ?',
                (name, location, contact, hospital_type, id))
            conn.commit()
        except sqlite3.OperationalError as e:
            return render_template('edit_hospital.html', hospital=hospital, error=f"Database error: {e}"), 500
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


# Add New Donation
@app.route('/donation/add', methods=['GET', 'POST'])
def add_donation():
    conn = get_db()
    donors = conn.execute('SELECT * FROM Donors').fetchall()
    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()
    if request.method == 'POST':
        donor_id = request.form['donor_id']
        hospital_id = request.form['hospital_id']
        donation_date = request.form['donation_date']
        blood_type = request.form['blood_type']
        status = request.form['status']
        try:
            conn.execute(
                'INSERT INTO Donations (DonorID, HospitalID, DonationDate, BloodType, Status) VALUES (?, ?, ?, ?, ?)',
                (donor_id, hospital_id, donation_date, blood_type, status))
            conn.commit()
            return redirect(url_for('admin_dashboard', success="Donation added successfully!"))
        except sqlite3.OperationalError as e:
            return render_template('add_donation.html', donors=donors, hospitals=hospitals,
                                   error=f"Database error: {e}"), 500
    return render_template('add_donation.html', donors=donors, hospitals=hospitals)


# Edit Donation
@app.route('/donation/edit/<int:id>', methods=['GET', 'POST'])
def edit_donation(id):
    conn = get_db()
    donation = conn.execute('SELECT * FROM Donations WHERE DonationID = ?', (id,)).fetchone()

    if not donation:
        return render_template('admin_dashboard.html', donors=conn.execute('SELECT * FROM Donors').fetchall(),
                               hospitals=conn.execute('SELECT * FROM Hospitals').fetchall(),
                               donations=conn.execute('SELECT * FROM Donations').fetchall(),
                               blood_requests=conn.execute('SELECT * FROM BloodRequests').fetchall(),
                               error="Donation not found."), 404

    if request.method == 'POST':
        donor_id = request.form['donor_id']
        hospital_id = request.form['hospital_id']
        donation_date = request.form['donation_date']
        blood_type = request.form['blood_type']
        status = request.form['status']
        try:
            conn.execute(
                'UPDATE Donations SET DonorID = ?, HospitalID = ?, DonationDate = ?, BloodType = ?, Status = ? WHERE DonationID = ?',
                (donor_id, hospital_id, donation_date, blood_type, status, id))
            conn.commit()
        except sqlite3.OperationalError as e:
            return render_template('edit_donation.html', donation=donation, error=f"Database error: {e}"), 500
        return redirect(url_for('admin_dashboard'))

    donors = conn.execute('SELECT * FROM Donors').fetchall()
    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()
    return render_template('edit_donation.html', donation=donation, donors=donors, hospitals=hospitals)


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
    blood_request = conn.execute('SELECT * FROM BloodRequests WHERE RequestID = ?', (id,)).fetchone()

    if not blood_request:
        return render_template('admin_dashboard.html', donors=conn.execute('SELECT * FROM Donors').fetchall(),
                               hospitals=conn.execute('SELECT * FROM Hospitals').fetchall(),
                               donations=conn.execute('SELECT * FROM Donations').fetchall(),
                               blood_requests=conn.execute('SELECT * FROM BloodRequests').fetchall(),
                               error="Blood request not found."), 404

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
            return render_template('edit_blood_request.html', blood_request=blood_request,
                                   error=f"Database error: {e}"), 500
        return redirect(url_for('admin_dashboard'))

    hospitals = conn.execute('SELECT * FROM Hospitals').fetchall()
    return render_template('edit_blood_request.html', blood_request=blood_request, hospitals=hospitals)


# Delete Blood Request
@app.route('/blood-request/delete/<int:id>')
def delete_blood_request(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM BloodRequests WHERE RequestID = ?', (id,))
        conn.commit()
    except sqlite3.OperationalError as e:
        return f"Database error: {e}", 500
    return redirect(url_for('admin_dashboard'))


# Add New Eligibility Check
@app.route('/eligibility/add', methods=['GET', 'POST'])
def add_eligibility():
    conn = get_db()
    donors = conn.execute('SELECT * FROM Donors').fetchall()
    if request.method == 'POST':
        donor_id = request.form['donor_id']
        last_eligibility_check = request.form['last_eligibility_check']
        eligibility_status = request.form['eligibility_status']
        try:
            conn.execute(
                'INSERT INTO DonationEligibility (DonorID, LastEligibilityCheck, EligibilityStatus) VALUES (?, ?, ?)',
                (donor_id, last_eligibility_check, eligibility_status))
            conn.commit()
            return redirect(url_for('admin_dashboard', success="Eligibility check added successfully!"))
        except sqlite3.OperationalError as e:
            return render_template('add_eligibility.html', donors=donors, error=f"Database error: {e}"), 500
    return render_template('add_eligibility.html', donors=donors)


# Edit Eligibility Check
@app.route('/eligibility/edit/<int:id>', methods=['GET', 'POST'])
def edit_eligibility(id):
    conn = get_db()
    eligibility = conn.execute('SELECT * FROM DonationEligibility WHERE EligibilityID = ?', (id,)).fetchone()

    if not eligibility:
        return render_template('admin_dashboard.html', donors=conn.execute('SELECT * FROM Donors').fetchall(),
                               hospitals=conn.execute('SELECT * FROM Hospitals').fetchall(),
                               donations=conn.execute('SELECT * FROM Donations').fetchall(),
                               blood_requests=conn.execute('SELECT * FROM BloodRequests').fetchall(),
                               error="Eligibility record not found."), 404

    if request.method == 'POST':
        donor_id = request.form['donor_id']
        last_eligibility_check = request.form['last_eligibility_check']
        eligibility_status = request.form['eligibility_status']
        try:
            conn.execute(
                'UPDATE DonationEligibility SET DonorID = ?, LastEligibilityCheck = ?, EligibilityStatus = ? WHERE EligibilityID = ?',
                (donor_id, last_eligibility_check, eligibility_status, id))
            conn.commit()
        except sqlite3.OperationalError as e:
            return render_template('edit_eligibility.html', eligibility=eligibility, error=f"Database error: {e}"), 500
        return redirect(url_for('admin_dashboard'))

    donors = conn.execute('SELECT * FROM Donors').fetchall()
    return render_template('edit_eligibility.html', eligibility=eligibility, donors=donors)


# Delete Eligibility Check
@app.route('/eligibility/delete開/<int:id>')
def delete_eligibility(id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM DonationEligibility WHERE EligibilityID = ?', (id,))
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


# Download Donations Report
@app.route('/download-donations-report')
def download_donations_report():
    # Implementation for downloading a CSV report (already present in your project)
    pass


# Organize a Blood Drive page
@app.route('/host-blood-drive', methods=['GET', 'POST'])
def host_blood_drive():
    conn = get_db()
    blood_drives = conn.execute('SELECT * FROM BloodDrives').fetchall()

    if request.method == 'POST':
        organizer_name = request.form['organizer_name']
        contact_info = request.form['contact_info']
        email = request.form['email']
        location = request.form['location']
        drive_date = request.form['drive_date']
        expected_donors = request.form['expected_donors']
        request_date = "2025-04-12"  # Current date (hardcoded for now; ideally use datetime.now())

        try:
            conn.execute(
                'INSERT INTO BloodDrives (OrganizerName, ContactInfo, Email, Location, DriveDate, ExpectedDonors, RequestDate) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (organizer_name, contact_info, email, location, drive_date, expected_donors, request_date))
            conn.commit()
            return render_template('host_blood_drive.html', active_page='host_blood_drive', blood_drives=blood_drives,
                                   success="Blood drive request submitted successfully!")
        except sqlite3.OperationalError as e:
            return render_template('host_blood_drive.html', active_page='host_blood_drive', blood_drives=blood_drives,
                                   error=f"Database error: {e}"), 500

    return render_template('host_blood_drive.html', active_page='host_blood_drive', blood_drives=blood_drives)


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

@app.route('/donations_for_donor/<int:donor_id>')
def donations_for_donor(donor_id):
    conn = get_db()
    donations = conn.execute('''
        SELECT Donations.*, Donors.Name AS DonorName, Hospitals.Name AS HospitalName
        FROM Donations
        JOIN Donors ON Donations.DonorID = Donors.DonorID
        JOIN Hospitals ON Donations.HospitalID = Hospitals.HospitalID
        WHERE Donations.DonorID = ?
    ''', (donor_id,)).fetchall()
    return render_template('donations_for_donor.html', donations=donations, donor_id=donor_id)


# Custom 404 Error Handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, port=5002)