-- Inserting into Donors Table
INSERT INTO Donors (Name, DateOfBirth, BloodType, ContactInfo, Email, LastDonationDate) VALUES
('John Doe', '1990-05-12', 'O+', '123-456-7890', 'johndoe@gmail.com', '2025-01-15'),
('Ashwini Smith', '1985-08-22', 'A-', '987-654-3210', 'ashwinismith@gmail.com', '2025-02-10'),
('Michael Brown', '1993-02-14', 'B+', '456-789-1230', 'michaelbrown@gmail.com', '2025-03-05'),
('Ananya Desai', '1993-06-11', 'AB-', '321-654-9870', 'ananyadesai@hotmail.com', '2024-12-20'),
('David Wilson', '1995-07-25', 'O-', '741-852-9630', 'davidwilson@gmail.com', '2025-02-28'),
('James Smith', '1992-09-10', 'A+', '369-258-1470', 'jamessmith@gmail.com', '2025-01-25');

SELECT * FROM Donors;

-- Inserting into Hospitals Table
INSERT INTO Hospitals (Name, Location, ContactInfo, HospitalType) VALUES
('City General Hospital', 'New York, NY', '212-555-1234', 'Public'),
('Sunrise Medical Center', 'Los Angeles, CA', '310-555-5678', 'Private'),
('Green Valley Clinic', 'Chicago, IL', '312-555-9012', 'Other'),
('St. Mary''s Hospital', 'Houston, TX', '713-555-3456', 'Military'),
('Hope Healthcare', 'Miami, FL', '305-555-7890', 'Public'),
('Evercare Hospital', 'San Francisco, CA', '415-555-6789', 'Private');

SELECT * FROM Hospitals;

-- Inserting into Donations Table
INSERT INTO Donations (DonorID, HospitalID, DonationDate, BloodType, Status) VALUES
(1, 1, '2025-01-15', 'O+', 'Completed'),
(1, 6, '2025-01-01', 'O+', 'Completed'),
(2, 6, '2025-03-01', 'A-', 'Completed'),
(2, 2, '2025-02-10', 'A-', 'Completed'),
(3, 3, '2025-03-05', 'B+', 'Scheduled'),
(3, 4, '2025-01-10', 'B+', 'Completed'),
(4, 4, '2024-12-20', 'AB-', 'Completed'),
(5, 4, '2025-03-05', 'O-', 'Completed'),
(5, 5, '2025-02-28', 'O-', 'Completed'),
(6, 6, '2025-01-25', 'A+', 'Scheduled');

SELECT * FROM Donations;

-- Inserting into DonationEligibility Table
INSERT INTO DonationEligibility (DonorID, LastEligibilityCheck, EligibilityStatus) VALUES
(1, '2025-03-10', 'Eligible'),
(2, '2025-03-15', 'Not Eligible'),
(3, '2025-03-20', 'Eligible'),
(4, '2025-02-28', 'Pending'),
(5, '2025-03-05', 'Eligible'),
(6, '2025-03-12', 'Not Eligible');

SELECT * FROM DonationEligibility;








