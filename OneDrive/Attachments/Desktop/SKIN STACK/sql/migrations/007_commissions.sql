-- Migration 007: Commissions table for commission calculations and payouts
-- Tracks influencer earnings with platform fees

CREATE TABLE IF NOT EXISTS commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    attribution_id UUID,  -- Can be NULL for direct attribution
    conversion_id UUID NOT NULL,
    influencer_id UUID NOT NULL,
    program_id UUID NOT NULL,

    -- Financial calculations
    order_amount DECIMAL(10,2) NOT NULL,  -- Base amount for commission
    commission_rate DECIMAL(5,4),  -- Rate applied (for percent type)
    gross_amount DECIMAL(10,2) NOT NULL,  -- Total commission before fees
    platform_fee_rate DECIMAL(5,4) DEFAULT 0.20,  -- 20% platform fee
    platform_fee DECIMAL(10,2) NOT NULL,
    net_amount DECIMAL(10,2) NOT NULL,  -- Amount influencer receives

    -- Status tracking
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'paid', 'cancelled', 'refunded')),
    approved_at TIMESTAMPTZ,
    approved_by UUID,  -- Admin user who approved

    -- Payout information
    paid_at TIMESTAMPTZ,
    payment_batch_id UUID,
    payment_method TEXT,
    payment_transaction_id TEXT,

    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_commissions_influencer_status ON commissions(influencer_id, status);
CREATE INDEX idx_commissions_conversion ON commissions(conversion_id);
CREATE INDEX idx_commissions_program ON commissions(program_id);
CREATE INDEX idx_commissions_status ON commissions(status);
CREATE INDEX idx_commissions_created_at ON commissions(created_at DESC);
CREATE INDEX idx_commissions_payment_batch ON commissions(payment_batch_id) WHERE payment_batch_id IS NOT NULL;

-- Payout aggregation index
CREATE INDEX idx_commissions_payout_ready ON commissions(influencer_id, net_amount)
    WHERE status = 'approved' AND paid_at IS NULL;

-- Foreign key constraints
ALTER TABLE commissions
    ADD CONSTRAINT fk_commissions_conversion
    FOREIGN KEY (conversion_id)
    REFERENCES conversions(id)
    ON DELETE CASCADE,

    ADD CONSTRAINT fk_commissions_influencer
    FOREIGN KEY (influencer_id)
    REFERENCES influencers(id)
    ON DELETE CASCADE,

    ADD CONSTRAINT fk_commissions_program
    FOREIGN KEY (program_id)
    REFERENCES programs(id)
    ON DELETE RESTRICT;

-- Update trigger
CREATE TRIGGER commissions_updated_at
    BEFORE UPDATE ON commissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Commission calculation function
CREATE OR REPLACE FUNCTION calculate_commission(
    p_conversion_id UUID,
    p_influencer_id UUID,
    p_program_id UUID
)
RETURNS TABLE(
    commission_id UUID,
    gross_amount DECIMAL,
    platform_fee DECIMAL,
    net_amount DECIMAL
) AS $$
DECLARE
    v_commission_id UUID;
    v_order_amount DECIMAL;
    v_commission_type TEXT;
    v_commission_value DECIMAL;
    v_gross DECIMAL;
    v_platform_fee_rate DECIMAL := 0.20;  -- 20% default
    v_platform_fee DECIMAL;
    v_net DECIMAL;
BEGIN
    -- Get order amount
    SELECT total INTO v_order_amount
    FROM conversions
    WHERE id = p_conversion_id;

    -- Get program commission settings
    SELECT commission_type, commission_value
    INTO v_commission_type, v_commission_value
    FROM programs
    WHERE id = p_program_id;

    -- Calculate gross commission
    IF v_commission_type = 'percent' THEN
        v_gross := v_order_amount * v_commission_value;
    ELSE  -- flat
        v_gross := v_commission_value;
    END IF;

    -- Calculate fees
    v_platform_fee := v_gross * v_platform_fee_rate;
    v_net := v_gross - v_platform_fee;

    -- Insert commission record
    INSERT INTO commissions (
        conversion_id, influencer_id, program_id,
        order_amount, commission_rate,
        gross_amount, platform_fee_rate, platform_fee, net_amount,
        status
    )
    VALUES (
        p_conversion_id, p_influencer_id, p_program_id,
        v_order_amount,
        CASE WHEN v_commission_type = 'percent' THEN v_commission_value ELSE NULL END,
        v_gross, v_platform_fee_rate, v_platform_fee, v_net,
        'pending'
    )
    RETURNING id INTO v_commission_id;

    RETURN QUERY SELECT v_commission_id, v_gross, v_platform_fee, v_net;
END;
$$ LANGUAGE plpgsql;

-- Payment batch table for bulk payouts
CREATE TABLE IF NOT EXISTS payment_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_number TEXT UNIQUE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    commission_count INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    processed_at TIMESTAMPTZ,
    processor_response JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payment_batches_status ON payment_batches(status);
CREATE INDEX idx_payment_batches_created ON payment_batches(created_at DESC);

-- Migration record
INSERT INTO schema_migrations (version, name)
VALUES (7, 'commissions')
ON CONFLICT (version) DO NOTHING;