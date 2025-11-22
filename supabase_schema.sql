-- Supabase Database Schema for Company Insight Chat UI
-- Run this in your Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    avatar_url TEXT,
    profile_summary TEXT,
    preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT DEFAULT 'New Chat',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User traits table (for future trait extraction)
CREATE TABLE IF NOT EXISTS user_traits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT,
    confidence FLOAT DEFAULT 0.0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, key)
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_traits ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.jwt() ->> 'email' = email);

CREATE POLICY "Users can insert own data" ON users
    FOR INSERT WITH CHECK (auth.jwt() ->> 'email' = email);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.jwt() ->> 'email' = email);

-- RLS Policies for sessions table
CREATE POLICY "Users can view own sessions" ON sessions
    FOR SELECT USING (
        user_id IN (SELECT id FROM users WHERE email = auth.jwt() ->> 'email')
    );

CREATE POLICY "Users can insert own sessions" ON sessions
    FOR INSERT WITH CHECK (
        user_id IN (SELECT id FROM users WHERE email = auth.jwt() ->> 'email')
    );

CREATE POLICY "Users can update own sessions" ON sessions
    FOR UPDATE USING (
        user_id IN (SELECT id FROM users WHERE email = auth.jwt() ->> 'email')
    );

CREATE POLICY "Users can delete own sessions" ON sessions
    FOR DELETE USING (
        user_id IN (SELECT id FROM users WHERE email = auth.jwt() ->> 'email')
    );

-- RLS Policies for messages table
CREATE POLICY "Users can view messages in own sessions" ON messages
    FOR SELECT USING (
        session_id IN (
            SELECT s.id FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE u.email = auth.jwt() ->> 'email'
        )
    );

CREATE POLICY "Users can insert messages in own sessions" ON messages
    FOR INSERT WITH CHECK (
        session_id IN (
            SELECT s.id FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE u.email = auth.jwt() ->> 'email'
        )
    );

-- RLS Policies for user_traits table
CREATE POLICY "Users can view own traits" ON user_traits
    FOR SELECT USING (
        user_id IN (SELECT id FROM users WHERE email = auth.jwt() ->> 'email')
    );

CREATE POLICY "Users can insert own traits" ON user_traits
    FOR INSERT WITH CHECK (
        user_id IN (SELECT id FROM users WHERE email = auth.jwt() ->> 'email')
    );

CREATE POLICY "Users can update own traits" ON user_traits
    FOR UPDATE USING (
        user_id IN (SELECT id FROM users WHERE email = auth.jwt() ->> 'email')
    );

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_user_traits_user_id ON user_traits(user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_traits_updated_at BEFORE UPDATE ON user_traits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
