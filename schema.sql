-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create categories table
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    point_value INTEGER DEFAULT 1,
    winner_id UUID, -- References nominees(id), will be added via ALTER TABLE later or inline if possible
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create nominees table
CREATE TABLE nominees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    name TEXT NOT NULL, -- The person or movie nominated
    movie TEXT, -- The movie associated with the nomination (can be null or same as name for Best Picture)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create picks table
CREATE TABLE picks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    nominee_id UUID REFERENCES nominees(id) ON DELETE CASCADE, -- Who they think will win
    want_nominee_id UUID REFERENCES nominees(id) ON DELETE CASCADE, -- Who they want to win
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    UNIQUE(user_id, category_id) -- A user can only make one pick per category
);

-- Row Level Security (RLS)
-- Since we are not dealing with proper auth, we will just enable RLS and allow anonymous access for now, or just leave RLS disabled.
-- Easiest for this simple app is to not enable RLS, as the Supabase key from Streamlit will have access.
