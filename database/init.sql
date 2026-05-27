CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    external_id INTEGER NOT NULL,  -- from filename (1,2,3,...)
    name TEXT NOT NULL,
    age TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    has_fingerprints BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE fingerprints (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL, -- from storage
    sex CHAR(1), -- M / F
    hand TEXT NOT NULL,   -- left / right
    finger TEXT NOT NULL, -- thumb, index, etc.
    filename TEXT NOT NULL, -- uploaded filename
    feature_vector vector(128),
    created_at TIMESTAMP DEFAULT NOW()
);