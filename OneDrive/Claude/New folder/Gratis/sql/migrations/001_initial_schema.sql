-- LevelUp Initial Database Schema
-- Run this in Neon SQL Editor: https://console.neon.tech

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Core User Tables
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  onboarding_completed BOOLEAN DEFAULT FALSE,
  timezone VARCHAR(50) DEFAULT 'UTC'
);

-- Avatar & Profile
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  avatar_id VARCHAR(50) NOT NULL,
  avatar_name VARCHAR(100) NOT NULL,
  selected_traits TEXT[] NOT NULL CHECK (array_length(selected_traits, 1) <= 3),
  quiz_answers JSONB NOT NULL DEFAULT '[]',
  trait_scores JSONB NOT NULL DEFAULT '{}',
  total_xp INTEGER DEFAULT 0,
  current_level INTEGER DEFAULT 1,
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  full_potential_progress DECIMAL(5,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id)
);

-- Goals
CREATE TABLE goals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  category VARCHAR(50) NOT NULL,
  cadence VARCHAR(20) NOT NULL CHECK (cadence IN ('daily', 'weekly', 'monthly')),
  target INTEGER,
  unit VARCHAR(50),
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8-Week Progression Plan
CREATE TABLE progression_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  week_number INTEGER NOT NULL CHECK (week_number BETWEEN 1 AND 8),
  tasks JSONB NOT NULL,
  min_time_minutes INTEGER NOT NULL,
  max_time_minutes INTEGER NOT NULL,
  difficulty_level VARCHAR(20) NOT NULL CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, week_number)
);

-- Daily Tasks
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  plan_id UUID REFERENCES progression_plans(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  trait VARCHAR(50) NOT NULL,
  difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
  xp_reward INTEGER NOT NULL,
  duration_minutes INTEGER NOT NULL,
  evidence_mode VARCHAR(20) NOT NULL CHECK (evidence_mode IN ('check', 'timer', 'photo')),
  scheduled_date DATE NOT NULL,
  completed BOOLEAN DEFAULT FALSE,
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Evidence Submissions
CREATE TABLE evidence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  evidence_type VARCHAR(20) NOT NULL CHECK (evidence_type IN ('check', 'timer', 'photo')),
  photo_url TEXT,
  timer_seconds INTEGER,
  notes TEXT,
  submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  is_valid BOOLEAN DEFAULT TRUE
);

-- Stakes & Financial Accountability (Web only)
CREATE TABLE stakes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  amount_cents INTEGER NOT NULL CHECK (amount_cents BETWEEN 100 AND 10000),
  model VARCHAR(20) NOT NULL CHECK (model IN ('flat', 'escalating')),
  destination VARCHAR(50) NOT NULL CHECK (destination IN ('charity', 'antiCharity', 'friend')),
  recipient_email VARCHAR(255),
  stripe_customer_id VARCHAR(255),
  stripe_payment_method_id VARCHAR(255),
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Grace & Charges
CREATE TABLE grace_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  week_start_date DATE NOT NULL,
  grace_used BOOLEAN DEFAULT FALSE,
  grace_used_at TIMESTAMP WITH TIME ZONE,
  daily_charge_used BOOLEAN DEFAULT FALSE,
  charge_amount_cents INTEGER,
  charge_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, week_start_date)
);

-- Party System (Social Features)
CREATE TABLE parties (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  code VARCHAR(20) UNIQUE NOT NULL,
  creator_id UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  active BOOLEAN DEFAULT TRUE
);

CREATE TABLE party_members (
  party_id UUID REFERENCES parties(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  role VARCHAR(20) DEFAULT 'member',
  PRIMARY KEY (party_id, user_id)
);

-- Analytics & Performance Metrics
CREATE TABLE user_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL,
  event_data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_tasks_user_date ON tasks(user_id, scheduled_date);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_evidence_task ON evidence(task_id);
CREATE INDEX idx_stakes_user_active ON stakes(user_id, active);
CREATE INDEX idx_analytics_user_event ON user_analytics(user_id, event_type);
CREATE INDEX idx_party_members_user ON party_members(user_id);

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add update triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_goals_updated_at BEFORE UPDATE ON goals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stakes_updated_at BEFORE UPDATE ON stakes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE stakes ENABLE ROW LEVEL SECURITY;
