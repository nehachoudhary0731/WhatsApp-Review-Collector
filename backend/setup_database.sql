-- Create database
CREATE DATABASE whatsapp_reviews;

-- Connect to the database and run this:
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    contact_number TEXT NOT NULL,
    user_name TEXT NOT NULL,
    product_name TEXT NOT NULL,
    product_review TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);