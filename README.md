# Blood Donation Management System

A web application for managing blood donations, built with Flask, SQLite, HTML/CSS, JavaScript, and TypeScript for the CS 665 Introduction to Database Systems course.

## Overview
This project is a CRUD application that manages blood donations, donors, and hospitals. It includes:
- A relational database using SQLite with 4 tables (Donors, Hospitals, Donations, DonationEligibility).
- A Flask-based web application with dashboards for donors, hospitals, and admins.
- CRUD operations for managing donors, hospitals, and donations.
- Predefined SQL queries (e.g., scheduled donations, eligible donors) with join operations.
- Frontend enhancements using TypeScript for form validation.

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/blood-donation-system.git
   cd blood-donation-system
   
pip install flask flask-sqlalchemy