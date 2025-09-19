-- Migration 002: Webhook Idempotency
-- Purpose: Prevent duplicate webhook processing with unique constraint on (source, external_event_id)
-- Target: Return 202 on duplicates, single conversion per event

-- Webhook events table for deduplication
CREATE TABLE IF NOT EXISTS webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL CHECK(source IN ('refersion', 'shopify', 'impact', 'levanta')),
    external_event_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    conversion_id UUID REFERENCES conversions(id) ON DELETE SET NULL,

    -- Response tracking
    status_code INTEGER DEFAULT 200,
    error_message TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CRITICAL: Unique index for idempotency
-- This ensures only one event per (source, external_event_id)
CREATE UNIQUE INDEX IF NOT EXISTS idx_webhook_events_idempotency
    ON webhook_events(source, external_event_id);

-- Performance index for lookups
CREATE INDEX IF NOT EXISTS idx_webhook_events_source_created
    ON webhook_events(source, created_at DESC);

-- Index for monitoring processing
CREATE INDEX IF NOT EXISTS idx_webhook_events_status
    ON webhook_events(status_code)
    WHERE status_code != 200;

-- Function to handle idempotent webhook processing
CREATE OR REPLACE FUNCTION process_webhook_idempotently(
    p_source TEXT,
    p_external_event_id TEXT,
    p_event_type TEXT,
    p_payload JSONB
) RETURNS TABLE(
    is_duplicate BOOLEAN,
    webhook_event_id UUID,
    conversion_id UUID
) AS $$
DECLARE
    v_webhook_id UUID;
    v_conversion_id UUID;
    v_is_duplicate BOOLEAN := false;
BEGIN
    -- Try to insert webhook event
    BEGIN
        INSERT INTO webhook_events (source, external_event_id, event_type, payload)
        VALUES (p_source, p_external_event_id, p_event_type, p_payload)
        RETURNING id INTO v_webhook_id;

        -- New event, not a duplicate
        v_is_duplicate := false;

    EXCEPTION WHEN unique_violation THEN
        -- Duplicate event, get existing record
        SELECT we.id, we.conversion_id INTO v_webhook_id, v_conversion_id
        FROM webhook_events we
        WHERE we.source = p_source
        AND we.external_event_id = p_external_event_id;

        v_is_duplicate := true;
    END;

    RETURN QUERY SELECT v_is_duplicate, v_webhook_id, v_conversion_id;
END;
$$ LANGUAGE plpgsql;

-- Add index to conversions for webhook lookups
CREATE INDEX IF NOT EXISTS idx_conversions_order_id
    ON conversions(order_id);

-- Migration record
INSERT INTO schema_migrations (version, name)
VALUES (2, 'webhook_idempotency')
ON CONFLICT (version) DO NOTHING;