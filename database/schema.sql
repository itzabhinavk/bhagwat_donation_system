-- ============================================================
-- schema.sql - Database Schema for Bhagwat Donation System
-- Run this file to create the database and tables
-- Usage: mysql -u root -p < schema.sql
-- ============================================================

-- Create the database if it doesn't exist

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

-- General Donations
CREATE TABLE IF NOT EXISTS general_donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reason VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    payment DECIMAL(12, 2) NOT NULL
);

-- Indexes for better query performance
CREATE INDEX idx_donations_donor ON donations(donor_name);
CREATE INDEX idx_donations_village ON donations(village);
CREATE INDEX idx_donations_date ON donations(donated_at);

-- ============================================================
-- Table: expense_ledger
-- Tracks all income (donations) and expenses for financial transparency
-- ============================================================
CREATE TABLE IF NOT EXISTS expense_ledger (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reason VARCHAR(255) NOT NULL,  -- कारण (Reason)
    date DATE NOT NULL,            -- तारीख (Date)
    payment_status DECIMAL(12, 2) NOT NULL,  -- भुगतान स्थिति (Payment Status: + for income, - for expense)
    balance DECIMAL(12, 2) NOT NULL,         -- वर्तमान शेष (Current Balance)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL,                 -- FK to admins.id
    FOREIGN KEY (created_by) REFERENCES admins(id) ON DELETE CASCADE
);

-- Indexes for expense ledger
CREATE INDEX idx_ledger_date ON expense_ledger(date);
CREATE INDEX idx_ledger_created_by ON expense_ledger(created_by);
