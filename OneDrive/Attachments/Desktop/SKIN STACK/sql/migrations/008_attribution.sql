-- Migration 008: Attribution table for conversion attribution
-- Links conversions to clicks and tracking links

CREATE TABLE IF NOT EXISTS attributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Core relationships
    conversion_id UUID NOT NULL,
    tracking_link_id UUID NOT NULL,
    click_id BIGINT,  -- References clicks table

    -- Attribution model
    model TEXT DEFAULT 'last_click' CHECK (model IN (
        'last_click',    -- Last touchpoint gets 100% credit
        'first_click',   -- First touchpoint gets 100% credit
        'linear',        -- Equal credit to all touchpoints
        'time_decay',    -- More credit to recent touchpoints
        'position_based' -- 40% first, 40% last, 20% middle
    )),

    -- Match confidence
    match_type TEXT CHECK (match_type IN (
        'subid',        -- Direct subid match (highest confidence)
        'device',       -- Device ID match
        'ip_time',      -- IP + time window match
        'cookie',       -- Cookie-based match
        'fingerprint'   -- Browser fingerprint match
    )),
    confidence_score DECIMAL(3,2) DEFAULT 1.0 CHECK (confidence_score BETWEEN 0 AND 1),

    -- Attribution window
    click_to_conversion_hours INTEGER,  -- Time between click and conversion
    within_cookie_window BOOLEAN DEFAULT true,

    -- Metadata
    reason TEXT,  -- Human-readable attribution reason
    attribution_path JSONB DEFAULT '[]',  -- Array of touchpoints
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_attributions_conversion ON attributions(conversion_id);
CREATE INDEX idx_attributions_tracking_link ON attributions(tracking_link_id);
CREATE INDEX idx_attributions_click ON attributions(click_id) WHERE click_id IS NOT NULL;
CREATE INDEX idx_attributions_model ON attributions(model);
CREATE INDEX idx_attributions_confidence ON attributions(confidence_score DESC);

-- Foreign key constraints
ALTER TABLE attributions
    ADD CONSTRAINT fk_attributions_conversion
    FOREIGN KEY (conversion_id)
    REFERENCES conversions(id)
    ON DELETE CASCADE,

    ADD CONSTRAINT fk_attributions_tracking_link
    FOREIGN KEY (tracking_link_id)
    REFERENCES tracking_links(id)
    ON DELETE CASCADE,

    ADD CONSTRAINT fk_attributions_click
    FOREIGN KEY (click_id)
    REFERENCES clicks(id)
    ON DELETE SET NULL;

-- Update commissions table to reference attributions
ALTER TABLE commissions
    ADD CONSTRAINT fk_commissions_attribution
    FOREIGN KEY (attribution_id)
    REFERENCES attributions(id)
    ON DELETE SET NULL;

-- Attribution matching function
CREATE OR REPLACE FUNCTION perform_attribution(
    p_conversion_id UUID,
    p_subid TEXT DEFAULT NULL,
    p_device_id TEXT DEFAULT NULL,
    p_ip_hash TEXT DEFAULT NULL
)
RETURNS TABLE(
    attribution_id UUID,
    tracking_link_id UUID,
    match_type TEXT,
    confidence DECIMAL
) AS $$
DECLARE
    v_attribution_id UUID;
    v_tracking_link_id UUID;
    v_click_id BIGINT;
    v_match_type TEXT;
    v_confidence DECIMAL;
    v_occurred_at TIMESTAMPTZ;
    v_cookie_window INTEGER;
BEGIN
    -- Get conversion timestamp
    SELECT occurred_at INTO v_occurred_at
    FROM conversions
    WHERE id = p_conversion_id;

    -- Priority 1: Direct subid match (highest confidence)
    IF p_subid IS NOT NULL THEN
        -- Extract slug from subid (format: influencerId_slug_timestamp)
        DECLARE
            v_slug TEXT;
        BEGIN
            v_slug := split_part(p_subid, '_', 2);

            SELECT tl.id INTO v_tracking_link_id
            FROM tracking_links tl
            WHERE tl.slug = v_slug
            LIMIT 1;

            IF v_tracking_link_id IS NOT NULL THEN
                v_match_type := 'subid';
                v_confidence := 1.0;

                -- Find associated click
                SELECT c.id INTO v_click_id
                FROM clicks c
                WHERE c.tracking_link_id = v_tracking_link_id
                    AND c.clicked_at < v_occurred_at
                ORDER BY c.clicked_at DESC
                LIMIT 1;

                -- Create attribution
                INSERT INTO attributions (
                    conversion_id, tracking_link_id, click_id,
                    model, match_type, confidence_score, reason
                )
                VALUES (
                    p_conversion_id, v_tracking_link_id, v_click_id,
                    'last_click', v_match_type, v_confidence,
                    'Direct subid match: ' || p_subid
                )
                RETURNING id INTO v_attribution_id;

                RETURN QUERY SELECT v_attribution_id, v_tracking_link_id, v_match_type, v_confidence;
                RETURN;
            END IF;
        END;
    END IF;

    -- Priority 2: Device ID match (high confidence)
    IF p_device_id IS NOT NULL THEN
        -- Get most recent click from this device within cookie window
        SELECT c.id, c.tracking_link_id, p.cookie_window_days
        INTO v_click_id, v_tracking_link_id, v_cookie_window
        FROM clicks c
        JOIN tracking_links tl ON c.tracking_link_id = tl.id
        JOIN programs p ON tl.program_id = p.id
        WHERE c.device_id = p_device_id
            AND c.clicked_at < v_occurred_at
            AND c.clicked_at > v_occurred_at - INTERVAL '1 day' * p.cookie_window_days
        ORDER BY c.clicked_at DESC
        LIMIT 1;

        IF v_tracking_link_id IS NOT NULL THEN
            v_match_type := 'device';
            v_confidence := 0.85;

            INSERT INTO attributions (
                conversion_id, tracking_link_id, click_id,
                model, match_type, confidence_score, reason
            )
            VALUES (
                p_conversion_id, v_tracking_link_id, v_click_id,
                'last_click', v_match_type, v_confidence,
                'Device ID match within cookie window'
            )
            RETURNING id INTO v_attribution_id;

            RETURN QUERY SELECT v_attribution_id, v_tracking_link_id, v_match_type, v_confidence;
            RETURN;
        END IF;
    END IF;

    -- Priority 3: IP + time window match (medium confidence)
    IF p_ip_hash IS NOT NULL THEN
        SELECT c.id, c.tracking_link_id
        INTO v_click_id, v_tracking_link_id
        FROM clicks c
        JOIN tracking_links tl ON c.tracking_link_id = tl.id
        WHERE c.ip_hash = p_ip_hash
            AND c.clicked_at < v_occurred_at
            AND c.clicked_at > v_occurred_at - INTERVAL '1 hour'
        ORDER BY c.clicked_at DESC
        LIMIT 1;

        IF v_tracking_link_id IS NOT NULL THEN
            v_match_type := 'ip_time';
            v_confidence := 0.60;

            INSERT INTO attributions (
                conversion_id, tracking_link_id, click_id,
                model, match_type, confidence_score, reason
            )
            VALUES (
                p_conversion_id, v_tracking_link_id, v_click_id,
                'last_click', v_match_type, v_confidence,
                'IP match within 1 hour window'
            )
            RETURNING id INTO v_attribution_id;

            RETURN QUERY SELECT v_attribution_id, v_tracking_link_id, v_match_type, v_confidence;
            RETURN;
        END IF;
    END IF;

    -- No attribution found
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- View for easy attribution reporting
CREATE OR REPLACE VIEW attribution_report AS
SELECT
    a.id as attribution_id,
    a.created_at as attributed_at,
    a.model,
    a.match_type,
    a.confidence_score,
    c.order_id,
    c.occurred_at as conversion_time,
    c.total as order_total,
    c.source as conversion_source,
    tl.slug as link_slug,
    i.name as influencer_name,
    i.email as influencer_email,
    p.name as program_name,
    m.name as merchant_name,
    cm.net_amount as commission_amount,
    cm.status as commission_status
FROM attributions a
JOIN conversions c ON a.conversion_id = c.id
JOIN tracking_links tl ON a.tracking_link_id = tl.id
JOIN influencers i ON tl.influencer_id = i.id
JOIN programs p ON tl.program_id = p.id
JOIN merchants m ON p.merchant_id = m.id
LEFT JOIN commissions cm ON cm.conversion_id = c.id AND cm.influencer_id = i.id;

-- Migration record
INSERT INTO schema_migrations (version, name)
VALUES (8, 'attribution')
ON CONFLICT (version) DO NOTHING;