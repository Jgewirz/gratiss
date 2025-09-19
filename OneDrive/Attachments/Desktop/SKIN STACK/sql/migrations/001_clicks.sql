-- Migration 001: Clicks table with performance-optimized indexes
-- Target: p50 ≤10ms for redirect, DB insert ≤2ms

-- First, create tracking_links table (minimal for now)
CREATE TABLE IF NOT EXISTS tracking_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    destination_url TEXT NOT NULL,
    influencer_id UUID,
    program_id UUID,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CRITICAL INDEX: slug lookup must be <5ms
-- Canonical: one active link per slug (idempotent)
CREATE UNIQUE INDEX IF NOT EXISTS idx_tracking_links_slug_active
    ON tracking_links(slug)
    WHERE is_active = true;

-- Read optimization: helps queries like WHERE slug = $1 AND is_active = true
CREATE INDEX IF NOT EXISTS idx_tracking_links_slug_is_active
    ON tracking_links(slug, is_active);

-- Clicks table optimized for write performance
CREATE TABLE IF NOT EXISTS clicks (
    id BIGSERIAL PRIMARY KEY,
    tracking_link_id UUID NOT NULL,

    -- Denormalized for query performance
    slug TEXT NOT NULL,

    -- Click metadata
    clicked_at TIMESTAMPTZ DEFAULT NOW(),
    ip INET,
    user_agent TEXT,
    referrer TEXT,
    device_id TEXT,

    -- UTM parameters as JSONB for flexibility
    utm_params JSONB,

    -- Session tracking
    session_id TEXT,

    -- Fraud signals (computed async)
    fraud_score DECIMAL(3,2) DEFAULT 0,
    is_bot BOOLEAN DEFAULT false
);

-- Primary index for attribution queries
CREATE INDEX IF NOT EXISTS idx_clicks_tracking_link_clicked
    ON clicks(tracking_link_id, clicked_at DESC);

-- Device-based attribution index
CREATE INDEX IF NOT EXISTS idx_clicks_device_clicked
    ON clicks(device_id, clicked_at DESC)
    WHERE device_id IS NOT NULL;

-- Session tracking index
CREATE INDEX IF NOT EXISTS idx_clicks_session
    ON clicks(session_id)
    WHERE session_id IS NOT NULL;

-- Time-based analytics index
CREATE INDEX IF NOT EXISTS idx_clicks_date
    ON clicks(clicked_at);

-- Insert trigger for metrics
CREATE OR REPLACE FUNCTION update_link_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update denormalized click count (async in production)
    UPDATE tracking_links
    SET total_clicks = total_clicks + 1
    WHERE id = NEW.tracking_link_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER clicks_update_metrics
    AFTER INSERT ON clicks
    FOR EACH ROW
    EXECUTE FUNCTION update_link_metrics();

-- Add column to tracking_links for metrics
ALTER TABLE tracking_links ADD COLUMN IF NOT EXISTS total_clicks INTEGER DEFAULT 0;

-- Migration record
INSERT INTO schema_migrations (version, name)
VALUES (1, 'clicks_optimized')
ON CONFLICT (version) DO NOTHING;