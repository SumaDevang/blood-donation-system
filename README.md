# Blood Donation Management System

## Introduction

The Blood Donation Management System is a web application designed to streamline the coordination and efficiency of blood donation processes. It provides a centralized platform for managing donor information, hospital blood requests, and donation records, ensuring a steady supply of blood for medical needs. The system supports multiple user roles, including donors, hospitals, and administrators, each with tailored functionalities to enhance their experience and operational effectiveness.

This project was developed as part of the CS 665 course for Spring 2025 at Wichita State University, focusing on database systems and web application development using Flask, SQLite, HTML, CSS, and Python.

## Setup Instructions
### Prerequisites
- Python 3.13 or higher
- SQLite
- Flask (`pip install flask`)

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/SumaDevang/blood-donation-system.git
   cd blood-donation-system
   

2. **Install Dependencies: Ensure you have Flask installed. If not, install it using:**:
   ```bash
   pip install flask
   
3. **Initialize the Database: The database is managed using SQLite. 
     Run the initialization script to create and populate the database::**:
   ```bash
   python init_db.py
This script uses create.sql to set up the schema and insert.sql to populate the database with initial data.
   
4. **Run the Application: Start the Flask application::**:
   ```bash
   python app.py
   
The application will be available at  http://127.0.0.1:5002

### Accessing the Application
Homepage: Visit  http://127.0.0.1:5002/ to access the homepage.

### Accessing the Application

After initializing the database and running the Flask application (see [Setup Instructions](#setup-instructions)), you can access the following pages:

- **Homepage**: [http://localhost:5000/](http://localhost:5000/) - Provides an overview of the system and role-based access descriptions.
- **Donor Registration**: [http://localhost:5000/donate-blood](http://localhost:5000/donate-blood) - Register as a new donor and access the Donor Dashboard.
- **Biomedical Services**: [http://localhost:5000/biomedical-services](http://localhost:5000/biomedical-services) - Learn about blood testing, storage, and distribution processes.
- **Data Insights**: [http://localhost:5000/insights](http://localhost:5000/insights) - Access predefined analytical queries organized into categories.
- **Dashboards**:
  - **Donor Dashboard**: [http://localhost:5000/donor](http://localhost:5000/donor) - Schedule donations, view donation history, and manage appointments.
  - **Hospital Dashboard**: [http://localhost:5000/hospital](http://localhost:5000/hospital) - Manage blood requests, track donation schedules, and search donors by blood type.
  - **Admin Dashboard**: [http://localhost:5000/admin](http://localhost:5000/admin) - Oversee system operations, manage all data, and generate reports.

### Features

- **Homepage**: Professional design with role-based access descriptions.
- **Donor Registration Page**: Register as a new donor and access the Donor Dashboard to manage your donations. Features a formal, professional design with success/error messages for better user feedback.
- **Donor Dashboard**: Schedule new donations, view your donation history, and manage upcoming appointments by entering your email. Now the central hub for all donor activities, with enhanced cancellation feedback.
- **Hospital Dashboard**: Manage blood requests, track donation schedules, and search donors by blood type requirements using a dedicated search form. Added Data Insights section with hospital-relevant queries (donors eligible for donation today, count of donors by blood type, latest completed donation for each hospital). Improved blood request form to correctly display hospital names in the dropdown.
- **Admin Dashboard**: Oversee system operations, manage all data (donors, hospitals, donations, blood requests, eligibility checks), and generate reports (system summary with 8 completed donations, completed donations by blood type totaling 8, donations per hospital with completed donations only, downloadable CSV). Added status filter to All Donations table and full CRUD operations for all tables. Fixed Edit and Delete functionality for donors to redirect to Admin Dashboard.
- **Insights Page**: A dedicated page accessible via the navigation bar, featuring predefined analytical queries organized into categories (Donor Insights, Hospital Insights, Donation Insights, Eligibility Insights). Includes a formal grid layout with collapsible sections for better readability and user experience. All queries involving donations now consider only completed donations for accuracy.
- **Biomedical Services**: Learn about blood testing, storage, distribution, quality assurance, and safety protocols, with statistics on total donations (11) and available blood units (8).
- **Error Handling**: Added a custom 404 error page for better user experience when accessing invalid routes.

### Project Structure
app.py: The main Flask application file containing all routes and logic.
init_db.py: Script to initialize the SQLite database using create.sql and insert.sql.
sql/create.sql: SQL script to create the database schema (tables for Donors, Hospitals, Donations, BloodRequests, etc.).
sql/insert.sql: SQL script to populate the database with initial data (10 donors, 6 hospitals, 8 completed donations, etc.).
templates/: Directory containing HTML templates for the application (e.g., index.html, admin_dashboard.html, donor_dashboard.html).
static/css/style.css: CSS file for styling the application with a formal, professional design.
static/js/script.js: JavaScript file for client-side validation (if any).
database.db: SQLite database file (generated after running init_db.py).
README.md: Project documentation (this file).
project.md: Additional project documentation (e.g., for CS 665 requirements).

### Database Schema
- **Donors**: Stores donor information (DonorID, Name, DateOfBirth, BloodType, ContactInfo, Email, LastDonationDate).
- **Hospitals**: Stores hospital information (HospitalID, Name, Location, ContactInfo, HospitalType).
- **Donations**: Stores donation records (DonationID, DonorID, HospitalID, DonationDate, BloodType, Status).
- **BloodRequests**: Stores blood requests by hospitals (RequestID, HospitalID, BloodType, Quantity, RequestDate).
- **DonationEligibility**: Stores donor eligibility status (DonorID, EligibilityStatus).

### Usage
### Donors:
Register as a new donor on the "Donor Registration" page.
Use the Donor Dashboard to schedule donations, view your donation history, and manage appointments.
### Hospitals:
Access the Hospital Dashboard to manage blood requests, track donation schedules, and search for donors by blood type.
### Administrators:
Use the Admin Dashboard to manage all data (donors, hospitals, donations, blood requests) and generate reports.
### Biomedical Services:
Learn about the processes involved in blood donation, including testing, storage, and distribution.

### Future Enhancements
### Authentication: 
Implement user authentication for donors, hospitals, and admins to secure access to dashboards.
### Advanced Reporting: 
Add more reports (e.g., blood requests by blood type, donations over time) to the Admin Dashboard.
### Responsive Design: 
Enhance the CSS to make the application fully responsive on mobile devices.

### Contributors
Suma Shekar (GitHub: https://github.com/SumaDevang)

