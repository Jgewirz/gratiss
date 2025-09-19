-- Migration 003: Conversions, Commissions, and Payouts tables
-- Purpose: Core financial tracking tables

-- Conversions table (idempotent)
CREATE TABLE IF NOT EXISTS conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_link_id UUID NOT NULL,
    click_id BIGINT REFERENCES clicks(id),

    -- Order details
    order_id TEXT NOT NULL,
    order_amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'USD',

    -- Attribution
    device_id TEXT,
    ip_hash TEXT,

    -- Timestamps
    converted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for conversions
CREATE INDEX IF NOT EXISTS idx_conversions_tracking_link
    ON conversions(tracking_link_id, converted_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversions_order_id
    ON conversions(order_id);

CREATE INDEX IF NOT EXISTS idx_conversions_click
    ON conversions(click_id)
    WHERE click_id IS NOT NULL;

-- Commissions table (idempotent - handle existing table)
CREATE TABLE IF NOT EXISTS commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversion_id UUID REFERENCES conversions(id) ON DELETE CASCADE,
    influencer_id UUID NOT NULL,

    -- Commission amounts
    gross_amount DECIMAL(10,2) NOT NULL,
    platform_fee_amount DECIMAL(10,2) NOT NULL, -- 20% of gross
    net_amount DECIMAL(10,2) NOT NULL, -- gross - platform_fee

    -- Status tracking
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'paid', 'disputed', 'cancelled')),

    -- Payment reference
    payout_id UUID,

    -- Timestamps
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add missing columns to existing commissions table
DO $$
BEGIN
    -- Add gross_amount if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commissions' AND column_name = 'gross_amount') THEN
        ALTER TABLE commissions ADD COLUMN gross_amount DECIMAL(10,2);
        UPDATE commissions SET gross_amount = amount WHERE gross_amount IS NULL AND amount IS NOT NULL;
    END IF;

    -- Add platform_fee_amount if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commissions' AND column_name = 'platform_fee_amount') THEN
        ALTER TABLE commissions ADD COLUMN platform_fee_amount DECIMAL(10,2);
        UPDATE commissions SET platform_fee_amount = platform_fee WHERE platform_fee_amount IS NULL AND platform_fee IS NOT NULL;
    END IF;

    -- Add calculated_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commissions' AND column_name = 'calculated_at') THEN
        ALTER TABLE commissions ADD COLUMN calculated_at TIMESTAMPTZ DEFAULT NOW();
    END IF;

    -- Add approved_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commissions' AND column_name = 'approved_at') THEN
        ALTER TABLE commissions ADD COLUMN approved_at TIMESTAMPTZ;
    END IF;

    -- Add paid_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commissions' AND column_name = 'paid_at') THEN
        ALTER TABLE commissions ADD COLUMN paid_at TIMESTAMPTZ;
    END IF;

    -- Add payout_id if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'commissions' AND column_name = 'payout_id') THEN
        ALTER TABLE commissions ADD COLUMN payout_id UUID;
    END IF;
END $$;

-- Indexes for commissions
CREATE INDEX IF NOT EXISTS idx_commissions_influencer
    ON commissions(influencer_id, status);

CREATE INDEX IF NOT EXISTS idx_commissions_conversion
    ON commissions(conversion_id);

CREATE INDEX IF NOT EXISTS idx_commissions_payout
    ON commissions(payout_id)
    WHERE payout_id IS NOT NULL;

-- Payouts table (idempotent)
CREATE TABLE IF NOT EXISTS payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID NOT NULL,

    -- Payout amounts
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 50.00), -- Min $50
    currency TEXT DEFAULT 'USD',

    -- Payment details
    payment_method TEXT CHECK (payment_method IN ('bank_transfer', 'paypal', 'stripe')),
    payment_reference TEXT, -- External payment ID

    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),

    -- Metadata
    commission_count INTEGER NOT NULL DEFAULT 0,
    notes TEXT,

    -- Timestamps
    initiated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for payouts
CREATE INDEX IF NOT EXISTS idx_payouts_influencer
    ON payouts(influencer_id, status);

CREATE INDEX IF NOT EXISTS idx_payouts_status
    ON payouts(status)
    WHERE status IN ('pending', 'processing');


-- Add foreign key from commissions to payouts if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'commissions_payout_id_fkey'
        AND table_name = 'commissions'
    ) THEN
        ALTER TABLE commissions
        ADD CONSTRAINT commissions_payout_id_fkey
        FOREIGN KEY (payout_id) REFERENCES payouts(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Migration record
INSERT INTO schema_migrations (version, name)
VALUES (3, 'conversions_commissions_payouts')
ON CONFLICT (version) DO NOTHING;