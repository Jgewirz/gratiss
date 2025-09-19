-- Migration 004: Merchants table for brand/store information
-- Stores merchant details and integration credentials

CREATE TABLE IF NOT EXISTS merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    domain TEXT UNIQUE,  -- Primary domain for matching
    website TEXT,

    -- Integration configuration
    integration_type TEXT,
    api_credentials JSONB DEFAULT '{}',  -- Encrypted in production
    webhook_secret TEXT,  -- For webhook signature verification

    -- Settings
    default_commission_type TEXT DEFAULT 'percent',
    default_commission_value DECIMAL(10,4) DEFAULT 0.10,  -- 10% default

    -- Status
    is_active BOOLEAN DEFAULT true,
    verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add missing columns if table already exists
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS name TEXT;
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS domain TEXT;
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS website TEXT;
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS integration_type TEXT;
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS api_credentials JSONB DEFAULT '{}';
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS webhook_secret TEXT;
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS default_commission_type TEXT DEFAULT 'percent';
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS default_commission_value DECIMAL(10,4) DEFAULT 0.10;
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS verified BOOLEAN DEFAULT false;
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Index for domain lookups
CREATE UNIQUE INDEX IF NOT EXISTS idx_merchants_domain ON merchants(domain) WHERE domain IS NOT NULL;

-- Index for active merchants
CREATE INDEX IF NOT EXISTS idx_merchants_active ON merchants(is_active) WHERE is_active = true;

-- Update trigger (drop and recreate to ensure correct definition)
DROP TRIGGER IF EXISTS merchants_updated_at ON merchants;
CREATE TRIGGER merchants_updated_at
    BEFORE UPDATE ON merchants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Add foreign key constraint to programs (if programs table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'programs') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
                      WHERE constraint_name = 'fk_programs_merchant') THEN
            ALTER TABLE programs
                ADD CONSTRAINT fk_programs_merchant
                FOREIGN KEY (merchant_id)
                REFERENCES merchants(id)
                ON DELETE CASCADE;
        END IF;
    END IF;
END
$$;

-- Add foreign key to tracking_links (if tracking_links table exists and has merchant_id column)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
              WHERE table_name = 'tracking_links' AND column_name = 'merchant_id') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
                      WHERE constraint_name = 'fk_tracking_links_merchant') THEN
            ALTER TABLE tracking_links
                ADD CONSTRAINT fk_tracking_links_merchant
                FOREIGN KEY (merchant_id)
                REFERENCES merchants(id)
                ON DELETE SET NULL;
        END IF;
    END IF;
END
$$;

-- Migration record
INSERT INTO schema_migrations (version, name)
VALUES (4, 'merchants')
ON CONFLICT (version) DO NOTHING;