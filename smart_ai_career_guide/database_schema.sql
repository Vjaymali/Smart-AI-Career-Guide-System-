CREATE DATABASE IF NOT EXISTS smart_ai_career_guide;
USE smart_ai_career_guide;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    age INT NOT NULL,
    mobile VARCHAR(20),
    verified TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Psychometric test results
CREATE TABLE IF NOT EXISTS psychometric_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    technical_score INT DEFAULT 0,
    social_score INT DEFAULT 0,
    creative_score INT DEFAULT 0,
    business_score INT DEFAULT 0,
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Career test results
CREATE TABLE IF NOT EXISTS career_test_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    top_subjects TEXT,
    weak_subjects TEXT,
    interests TEXT,
    skills TEXT,
    relocation VARCHAR(10),
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Career predictions/results
CREATE TABLE IF NOT EXISTS career_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    primary_career VARCHAR(255),
    primary_confidence DECIMAL(5,2),
    primary_score DECIMAL(5,2),
    secondary_career VARCHAR(255),
    secondary_confidence DECIMAL(5,2),
    secondary_score DECIMAL(5,2),
    alternative_career VARCHAR(255),
    alternative_confidence DECIMAL(5,2),
    alternative_score DECIMAL(5,2),
    academic_score DECIMAL(5,2),
    psychometric_score DECIMAL(5,2),
    interest_score DECIMAL(5,2),
    result_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Chatbot conversation history
CREATE TABLE IF NOT EXISTS chat_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Career advisor bookings
CREATE TABLE IF NOT EXISTS advisor_bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    preferred_date DATE,
    preferred_time VARCHAR(50),
    message TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
"
Observation: Create successful: /app/flask_backend/database_schema.sql