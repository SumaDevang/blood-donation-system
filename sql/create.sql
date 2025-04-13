
-- Creating Donors Table-Information about the blood donors
CREATE TABLE Donors (
    DonorID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    DateOfBirth DATE NOT NULL,
    BloodType TEXT NOT NULL CHECK (BloodType IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    ContactInfo TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    LastDonationDate DATE
);

-- Creating Hospitals Table - Information about hospitals requiring blood
CREATE TABLE Hospitals (
    HospitalID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Location TEXT NOT NULL,
    ContactInfo TEXT NOT NULL,
    HospitalType TEXT NOT NULL CHECK (HospitalType IN ('Public', 'Private', 'Military', 'Other'))
);

-- Creating BloodRequests Table - Records of blood requests by hospitals
CREATE TABLE BloodRequests (
    RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
    HospitalID INTEGER NOT NULL,
    BloodType TEXT NOT NULL CHECK (BloodType IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    Quantity INTEGER NOT NULL CHECK (Quantity > 0),
    RequestDate DATE NOT NULL,
    FOREIGN KEY (HospitalID) REFERENCES Hospitals(HospitalID) ON DELETE CASCADE
);

-- Creating Donations Table - Records of blood donations
CREATE TABLE Donations (
    DonationID INTEGER PRIMARY KEY AUTOINCREMENT,
    DonorID INTEGER NOT NULL,
    HospitalID INTEGER NOT NULL,
    DonationDate DATE NOT NULL,
    BloodType TEXT NOT NULL,
    Status TEXT NOT NULL CHECK (Status IN ('Completed', 'Scheduled')),
    FOREIGN KEY (DonorID) REFERENCES Donors(DonorID) ON DELETE CASCADE,
    FOREIGN KEY (HospitalID) REFERENCES Hospitals(HospitalID) ON DELETE CASCADE
);


-- Creating DonationEligibility Table - Donor eligibility tracking
CREATE TABLE DonationEligibility (
    EligibilityID INTEGER PRIMARY KEY AUTOINCREMENT,
    DonorID INTEGER NOT NULL,
    LastEligibilityCheck DATE NOT NULL,
    EligibilityStatus TEXT NOT NULL CHECK (EligibilityStatus IN ('Eligible', 'Not Eligible', 'Pending')),
    FOREIGN KEY (DonorID) REFERENCES Donors(DonorID) ON DELETE CASCADE
);




