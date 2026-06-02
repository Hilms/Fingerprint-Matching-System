CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE subjects (
    external_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    age INTEGER,
    address TEXT,
    city TEXT,
    country TEXT,
    phone_number TEXT,
    has_fingerprints BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE fingerprints (
    id SERIAL PRIMARY KEY,
    subject_external_id INTEGER REFERENCES subjects(external_id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    sex CHAR(1),
    hand TEXT NOT NULL,
    finger TEXT NOT NULL,
    filename TEXT NOT NULL,
    feature_vector vector(128) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);