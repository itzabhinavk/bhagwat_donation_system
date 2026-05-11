-- ============================================================
-- schema.sql - Database Schema for Bhagwat Donation System
-- Run this file to create the database and tables
-- Usage: mysql -u root -p < schema.sql
-- ============================================================

-- Create the database if it doesn't exist
--CREATE DATABASE IF NOT EXISTS bhagwat_db
 --   CHARACTER SET utf8mb4
 --   COLLATE utf8mb4_unicode_ci;

--USE bhagwat_db;

-- ============================================================
-- Table: admins
-- Stores admin login credentials and session tracking
-- ============================================================
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,          -- Werkzeug hashed password
    active_session VARCHAR(255) DEFAULT NULL, -- Current session token (only one allowed)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Table: donations
-- Stores all donation records entered by admin
-- ============================================================
CREATE TABLE IF NOT EXISTS donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_name VARCHAR(200) NOT NULL,
    village VARCHAR(200) NOT NULL,
    donor_contact VARCHAR(150) DEFAULT NULL,
    campaign VARCHAR(255) DEFAULT 'General',
    amount DECIMAL(12, 2) NOT NULL,
    payment_method ENUM('Cash', 'Online', 'Cheque', 'Other') DEFAULT 'Cash',
    payment_status ENUM('Received', 'Pending', 'Cancelled') DEFAULT 'Received',
    remark TEXT DEFAULT NULL,
    donated_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Table: notices
-- Stores public notices/announcements shown on homepage
-- ============================================================
CREATE TABLE IF NOT EXISTS notices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Table: donation_tables
-- Stores metadata and display labels for static donation tables
-- ============================================================
CREATE TABLE IF NOT EXISTS donation_tables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_key VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(500) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT IGNORE INTO donation_tables (table_key, title, description) VALUES
  ('temple_donations', 'Temple Donations', 'Donations for the temple and rituals'),
  ('annadan_fund', 'Annadan Fund', 'Contributions for free food distribution'),
  ('prasadam_collection', 'Prasadam Collection', 'Funds collected for prasadam preparation'),
  ('cultural_programs', 'Cultural Programs', 'Support for cultural events and programs'),
  ('maintenance_fund', 'Maintenance Fund', 'Donations for temple maintenance and repairs'),
  ('education_support', 'Education Support', 'Support for education-related initiatives'),
  ('general_donations', 'General Donations', 'General offering and charity donations');

-- ============================================================
-- Additional Donation Tables (7 static tables)
-- ============================================================

-- Temple Donations
CREATE TABLE IF NOT EXISTS temple_donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_name VARCHAR(200) NOT NULL,
    village VARCHAR(200) NOT NULL,
    donor_contact VARCHAR(150) DEFAULT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method ENUM('Cash', 'Online', 'Cheque', 'Other') DEFAULT 'Cash',
    payment_status ENUM('Received', 'Pending', 'Cancelled') DEFAULT 'Received',
    remark TEXT DEFAULT NULL,
    donated_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Annadan Fund
CREATE TABLE IF NOT EXISTS annadan_fund (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_name VARCHAR(200) NOT NULL,
    village VARCHAR(200) NOT NULL,
    donor_contact VARCHAR(150) DEFAULT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method ENUM('Cash', 'Online', 'Cheque', 'Other') DEFAULT 'Cash',
    payment_status ENUM('Received', 'Pending', 'Cancelled') DEFAULT 'Received',
    remark TEXT DEFAULT NULL,
    donated_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prasadam Collection
CREATE TABLE IF NOT EXISTS prasadam_collection (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_name VARCHAR(200) NOT NULL,
    village VARCHAR(200) NOT NULL,
    donor_contact VARCHAR(150) DEFAULT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method ENUM('Cash', 'Online', 'Cheque', 'Other') DEFAULT 'Cash',
    payment_status ENUM('Received', 'Pending', 'Cancelled') DEFAULT 'Received',
    remark TEXT DEFAULT NULL,
    donated_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cultural Programs
CREATE TABLE IF NOT EXISTS cultural_programs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_name VARCHAR(200) NOT NULL,
    village VARCHAR(200) NOT NULL,
    donor_contact VARCHAR(150) DEFAULT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method ENUM('Cash', 'Online', 'Cheque', 'Other') DEFAULT 'Cash',
    payment_status ENUM('Received', 'Pending', 'Cancelled') DEFAULT 'Received',
    remark TEXT DEFAULT NULL,
    donated_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Maintenance Fund
CREATE TABLE IF NOT EXISTS maintenance_fund (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_name VARCHAR(200) NOT NULL,
    village VARCHAR(200) NOT NULL,
    donor_contact VARCHAR(150) DEFAULT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method ENUM('Cash', 'Online', 'Cheque', 'Other') DEFAULT 'Cash',
    payment_status ENUM('Received', 'Pending', 'Cancelled') DEFAULT 'Received',
    remark TEXT DEFAULT NULL,
    donated_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Education Support
CREATE TABLE IF NOT EXISTS education_support (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_name VARCHAR(200) NOT NULL,
    village VARCHAR(200) NOT NULL,
    donor_contact VARCHAR(150) DEFAULT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method ENUM('Cash', 'Online', 'Cheque', 'Other') DEFAULT 'Cash',
    payment_status ENUM('Received', 'Pending', 'Cancelled') DEFAULT 'Received',
    remark TEXT DEFAULT NULL,
    donated_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- General Donations
CREATE TABLE IF NOT EXISTS general_donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_name VARCHAR(200) NOT NULL,
    village VARCHAR(200) NOT NULL,
    donor_contact VARCHAR(150) DEFAULT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method ENUM('Cash', 'Online', 'Cheque', 'Other') DEFAULT 'Cash',
    payment_status ENUM('Received', 'Pending', 'Cancelled') DEFAULT 'Received',
    remark TEXT DEFAULT NULL,
    donated_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_donations_donor ON donations(donor_name);
CREATE INDEX IF NOT EXISTS idx_donations_village ON donations(village);
CREATE INDEX IF NOT EXISTS idx_donations_date ON donations(donated_at);
