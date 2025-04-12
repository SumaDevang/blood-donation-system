==============================================
-- CRUD Operations
-- ==============================================

-- ==============================================
-- CREATE: Insert new records into each table
-- ==============================================
SELECT * FROM Donors;

-- Insert a new donor
INSERT INTO Donors (Name, DateOfBirth, BloodType, ContactInfo, Email, LastDonationDate) 
VALUES ('Emma Watson', '1991-04-15', 'B-', '555-321-9876', 'emmawatson@example.com', '2025-03-10');

SELECT * FROM Donors;

SELECT * FROM Hospitals;

-- Insert a new hospital
INSERT INTO Hospitals (Name, Location, ContactInfo, HospitalType) 
VALUES ('Mercy Hospital', 'Dallas, TX', '214-555-7890', 'Public');

SELECT * FROM Hospitals;

SELECT * FROM Donations;

-- Insert a new donation record
INSERT INTO Donations (DonorID, HospitalID, DonationDate, BloodType, Status) 
VALUES (1, 1, '2025-03-20', 'O+', 'Scheduled');

SELECT * FROM Donations;

SELECT * FROM DonationEligibility;

-- Insert a new eligibility check record
INSERT INTO DonationEligibility (DonorID, LastEligibilityCheck, EligibilityStatus) 
VALUES (1, '2025-03-28', 'Eligible');

SELECT * FROM DonationEligibility;

-- ==============================================
-- READ: Retrieve data using SELECT queries
-- ==============================================

-- Retrieve all donors
SELECT * FROM Donors;

-- Retrieve all hospitals
SELECT * FROM Hospitals;

-- Retrieve donation records for a specific donor
SELECT * FROM Donations WHERE DonorID = 1;

-- Retrieve eligible donors
SELECT Donors.Name, DonationEligibility.EligibilityStatus 
FROM Donors 
JOIN DonationEligibility ON Donors.DonorID = DonationEligibility.DonorID
WHERE EligibilityStatus = 'Eligible';

-- Retrieve all scheduled donations with donor and hospital details
SELECT Donors.Name, Hospitals.Name AS HospitalName, Donations.DonationDate, Donations.Status 
FROM Donations 
JOIN Donors ON Donations.DonorID = Donors.DonorID
JOIN Hospitals ON Donations.HospitalID = Hospitals.HospitalID
WHERE Donations.Status = 'Scheduled';

-- ==============================================
-- UPDATE: Modify existing records
-- ==============================================

-- Update a donor's contact info
UPDATE Donors 
SET ContactInfo = '555-888-9999' 
WHERE DonorID = 1;

SELECT * FROM Donors;

-- Update donation status to "Completed"
UPDATE Donations 
SET Status = 'Completed' 
WHERE DonationID = 1;

SELECT * FROM Donations;

-- Update hospital location
UPDATE Hospitals 
SET Location = 'Austin, TX' 
WHERE HospitalID = 1;

SELECT * FROM Hospitals;

-- Update a donor's eligibility status
UPDATE DonationEligibility 
SET EligibilityStatus = 'Not Eligible' 
WHERE DonorID = 1;

SELECT * FROM DonationEligibility;

-- ==============================================
-- DELETE: Remove records from tables
-- ==============================================


-- Delete a specific donor
DELETE FROM Donors WHERE DonorID = 6;

SELECT * FROM Donors;

-- Delete all donations for a specific donor
DELETE FROM Donations WHERE DonorID = 2;

SELECT * FROM Donations;

-- Delete a hospital by ID
DELETE FROM Hospitals WHERE HospitalID = 3;

SELECT * FROM Hospitals;

-- Delete an eligibility record
DELETE FROM DonationEligibility WHERE EligibilityID = 1;

SELECT * FROM DonationEligibility;

