-- Migration 006: Conversions table for order/conversion tracking
-- Stores conversion events with idempotency guarantees

CREATE TABLE IF NOT EXISTS conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Idempotency keys
    order_id TEXT NOT NULL,
    source TEXT NOT NULL,  -- shopify, impact, amazon, etc.
    external_event_id TEXT,  -- External system's event ID

    -- Timing
    occurred_at TIMESTAMPTZ NOT NULL,
    reported_at TIMESTAMPTZ DEFAULT NOW(),

    -- Financial data
    subtotal DECIMAL(10,2),
    tax DECIMAL(10,2) DEFAULT 0,
    shipping DECIMAL(10,2) DEFAULT 0,
    discount DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'USD',

    -- Line items and metadata
    items JSONB DEFAULT '[]',  -- Array of {product_id, quantity, price}
    customer_info JSONB DEFAULT '{}',  -- {email, location, etc} - hashed/encrypted

    -- Attribution data
    subid TEXT,  -- Our tracking parameter
    device_id TEXT,
    ip_hash TEXT,
    landing_page TEXT,
    referrer TEXT,

    -- Raw webhook data for debugging
    raw_event JSONB,

    -- Processing status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'refunded')),
    rejection_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Idempotency constraint
    CONSTRAINT conversions_idempotency UNIQUE(source, order_id),
    CONSTRAINT conversions_external_id UNIQUE(source, external_event_id)
);

-- Performance indexes
CREATE INDEX idx_conversions_order_id ON conversions(order_id);
CREATE INDEX idx_conversions_occurred_at ON conversions(occurred_at DESC);
CREATE INDEX idx_conversions_subid ON conversions(subid) WHERE subid IS NOT NULL;
CREATE INDEX idx_conversions_device_id ON conversions(device_id) WHERE device_id IS NOT NULL;
CREATE INDEX idx_conversions_status ON conversions(status);
CREATE INDEX idx_conversions_source ON conversions(source);

-- Analytics index for date ranges
CREATE INDEX idx_conversions_date_range ON conversions(occurred_at, status)
    WHERE status IN ('approved', 'pending');

-- Update trigger
CREATE TRIGGER conversions_updated_at
    BEFORE UPDATE ON conversions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Idempotent conversion processing function
CREATE OR REPLACE FUNCTION process_conversion_idempotently(
    p_source TEXT,
    p_order_id TEXT,
    p_external_event_id TEXT,
    p_occurred_at TIMESTAMPTZ,
    p_total DECIMAL,
    p_subid TEXT,
    p_raw_event JSONB
)
RETURNS TABLE(
    conversion_id UUID,
    is_duplicate BOOLEAN,
    existing_status TEXT
) AS $$
DECLARE
    v_conversion_id UUID;
    v_is_duplicate BOOLEAN := false;
    v_existing_status TEXT;
BEGIN
    -- Try to insert, handling duplicates
    INSERT INTO conversions (
        source, order_id, external_event_id, occurred_at,
        total, subid, raw_event, status
    )
    VALUES (
        p_source, p_order_id, p_external_event_id, p_occurred_at,
        p_total, p_subid, p_raw_event, 'pending'
    )
    ON CONFLICT (source, order_id) DO UPDATE
        SET updated_at = NOW()
    RETURNING id, status INTO v_conversion_id, v_existing_status;

    -- Check if this was a duplicate
    IF NOT FOUND THEN
        SELECT id, status, true
        INTO v_conversion_id, v_existing_status, v_is_duplicate
        FROM conversions
        WHERE source = p_source AND order_id = p_order_id;
    END IF;

    RETURN QUERY SELECT v_conversion_id, v_is_duplicate, v_existing_status;
END;
$$ LANGUAGE plpgsql;

-- Migration record
INSERT INTO schema_migrations (version, name)
VALUES (6, 'conversions')
ON CONFLICT (version) DO NOTHING;