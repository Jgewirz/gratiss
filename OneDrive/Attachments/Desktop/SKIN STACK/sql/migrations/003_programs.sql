-- Migration 003: Programs table for affiliate program configuration
-- Stores commission structures and integration settings

CREATE TABLE IF NOT EXISTS programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL,
    name TEXT NOT NULL,
    description TEXT,

    -- Commission configuration
    commission_type TEXT NOT NULL CHECK (commission_type IN ('percent', 'flat')),
    commission_value DECIMAL(10,4) NOT NULL CHECK (commission_value > 0),
    cookie_window_days INTEGER DEFAULT 7 CHECK (cookie_window_days > 0),

    -- Integration details
    website TEXT,
    integration_type TEXT CHECK (integration_type IN ('shopify_refersion', 'impact', 'amazon', 'levanta', 'custom')),

    -- Status
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for active programs lookup
CREATE INDEX IF NOT EXISTS idx_programs_active ON programs(is_active) WHERE is_active = true;

-- Index for merchant relationship
CREATE INDEX IF NOT EXISTS idx_programs_merchant ON programs(merchant_id);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS programs_updated_at ON programs;
CREATE TRIGGER programs_updated_at
    BEFORE UPDATE ON programs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Add merchant_id to tracking_links if not exists
ALTER TABLE tracking_links ADD COLUMN IF NOT EXISTS merchant_id UUID;
ALTER TABLE tracking_links ADD COLUMN IF NOT EXISTS product_id UUID;
ALTER TABLE tracking_links ADD COLUMN IF NOT EXISTS campaign_id UUID;
ALTER TABLE tracking_links ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE tracking_links ADD COLUMN IF NOT EXISTS utm_source TEXT;
ALTER TABLE tracking_links ADD COLUMN IF NOT EXISTS utm_medium TEXT;
ALTER TABLE tracking_links ADD COLUMN IF NOT EXISTS utm_campaign TEXT;

-- Migration record
INSERT INTO schema_migrations (version, name)
VALUES (3, 'programs')
ON CONFLICT (version) DO NOTHING;