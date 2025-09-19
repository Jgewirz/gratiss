-- Migration 005: Influencers table for content creator profiles
-- Stores influencer information and payment details

CREATE TABLE IF NOT EXISTS influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identity
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    username TEXT UNIQUE,  -- Platform-agnostic username/handle

    -- Social platforms
    platform_handles JSONB DEFAULT '{}',  -- {"instagram": "@handle", "tiktok": "@user", "youtube": "channel_id"}
    audience_metrics JSONB DEFAULT '{}',  -- {"instagram_followers": 10000, "engagement_rate": 0.05}

    -- Payment (encrypted in production)
    payment_info JSONB DEFAULT '{}',  -- {"method": "paypal", "account": "email@example.com"}
    tax_info JSONB DEFAULT '{}',  -- {"ssn_last4": "1234", "tax_form": "W9"}

    -- Payout settings
    min_payout_amount DECIMAL(10,2) DEFAULT 50.00,
    payout_frequency TEXT DEFAULT 'monthly' CHECK (payout_frequency IN ('weekly', 'biweekly', 'monthly', 'manual')),

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('pending', 'active', 'paused', 'terminated')),
    tier TEXT DEFAULT 'bronze' CHECK (tier IN ('bronze', 'silver', 'gold', 'platinum')),

    -- Metadata
    notes TEXT,
    tags TEXT[],  -- Array of tags for categorization
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_influencers_email ON influencers(email);
CREATE INDEX idx_influencers_username ON influencers(username) WHERE username IS NOT NULL;
CREATE INDEX idx_influencers_status ON influencers(status);
CREATE INDEX idx_influencers_tags ON influencers USING GIN(tags) WHERE tags IS NOT NULL;

-- Update trigger
CREATE TRIGGER influencers_updated_at
    BEFORE UPDATE ON influencers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Add foreign key to tracking_links
ALTER TABLE tracking_links
    ADD CONSTRAINT fk_tracking_links_influencer
    FOREIGN KEY (influencer_id)
    REFERENCES influencers(id)
    ON DELETE CASCADE;

-- Create products table (referenced by tracking_links)
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    sku TEXT,
    url TEXT,
    image_url TEXT,
    price DECIMAL(10,2),
    category TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(merchant_id, sku)
);

-- Product indexes
CREATE INDEX idx_products_merchant ON products(merchant_id);
CREATE INDEX idx_products_sku ON products(sku) WHERE sku IS NOT NULL;
CREATE INDEX idx_products_active ON products(is_active) WHERE is_active = true;

-- Product update trigger
CREATE TRIGGER products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Add product foreign key to tracking_links
ALTER TABLE tracking_links
    ADD CONSTRAINT fk_tracking_links_product
    FOREIGN KEY (product_id)
    REFERENCES products(id)
    ON DELETE SET NULL;

-- Migration record
INSERT INTO schema_migrations (version, name)
VALUES (5, 'influencers_and_products')
ON CONFLICT (version) DO NOTHING;