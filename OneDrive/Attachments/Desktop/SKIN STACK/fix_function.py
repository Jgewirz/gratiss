#!/usr/bin/env python3
"""Fix the webhook idempotency function"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://neondb_owner:npg_QlUFO3LdE5zn@ep-orange-night-admridz5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

async def fix_function():
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Drop and recreate the function with fix
        await conn.execute("DROP FUNCTION IF EXISTS process_webhook_idempotently CASCADE")
        print("[OK] Dropped old function")

        await conn.execute("""
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
        """)
        print("[OK] Recreated function with fix")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_function())