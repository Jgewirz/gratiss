"""Webhook handlers with idempotency and signature validation"""
from fastapi import APIRouter, HTTPException, Response, Request, Header, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from decimal import Decimal
import asyncpg
import logging
from datetime import datetime
import os

from lib.db import db
from lib.websocket_manager import manager
from lib.webhook_security import WebhookValidator

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

# Initialize webhook validator
webhook_secret = os.getenv("REFERSION_WEBHOOK_SECRET", "dev_secret_change_in_production")
validator = WebhookValidator(webhook_secret)

class RefersionWebhook(BaseModel):
    """Refersion webhook payload"""
    event_type: str
    event_id: str  # External event ID for idempotency
    order_id: str
    affiliate_id: str
    commission_amount: Decimal
    sale_amount: Decimal
    currency: str = "USD"
    tracking_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@router.post("/refersion")
async def handle_refersion_webhook(
    webhook: RefersionWebhook,
    request: Request,
    response: Response,
    x_refersion_signature: Optional[str] = Header(None)
):
    """
    Handle Refersion webhook with idempotency and signature validation.
    Returns 202 Accepted for duplicate events.
    """
    # Validate webhook signature in production
    if os.getenv("ENVIRONMENT", "development") == "production":
        if not x_refersion_signature:
            raise HTTPException(
                status_code=401,
                detail="Missing webhook signature"
            )

        # Get raw body for signature validation
        body = await request.body()

        # Parse signature header (format: sha256=<signature>)
        try:
            algorithm, signature = x_refersion_signature.split("=", 1)
            if algorithm != "sha256":
                raise ValueError("Unsupported algorithm")
        except ValueError:
            raise HTTPException(
                status_code=401,
                detail="Invalid signature format"
            )

        # Validate signature
        if not validator.validate_signature(body, signature):
            logger.warning(f"Invalid webhook signature from {request.client.host}")
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature"
            )
    else:
        # Development mode - log warning
        if not x_refersion_signature:
            logger.warning("Webhook received without signature (dev mode)")
    # Use the global db instance

    async with db.pool.acquire() as conn:
        try:
            # Check for duplicate using idempotent function
            import json
            # Convert webhook to dict, converting Decimal to float
            webhook_data = webhook.dict()
            webhook_data['commission_amount'] = float(webhook.commission_amount)
            webhook_data['sale_amount'] = float(webhook.sale_amount)

            result = await conn.fetchrow("""
                SELECT * FROM process_webhook_idempotently(
                    $1, $2, $3, $4::jsonb
                )
            """, "refersion", webhook.event_id, webhook.event_type, json.dumps(webhook_data))

            if result['is_duplicate']:
                # Duplicate event - return 202 Accepted
                logger.info(f"Duplicate webhook received: {webhook.event_id}")
                response.status_code = 202

                # Broadcast duplicate webhook event
                await manager.broadcast_webhook(
                    source="refersion",
                    event_type=webhook.event_type,
                    status="duplicate",
                    event_id=webhook.event_id
                )
                return {
                    "status": "accepted",
                    "message": "Event already processed",
                    "webhook_event_id": str(result['webhook_event_id']),
                    "conversion_id": str(result['conversion_id']) if result['conversion_id'] else None
                }

            # Process new webhook - create conversion
            async with conn.transaction():
                # Find tracking link by affiliate_id or tracking_id
                tracking_link = await conn.fetchrow("""
                    SELECT tl.id, tl.influencer_id, p.commission_rate
                    FROM tracking_links tl
                    JOIN programs p ON p.id = tl.program_id
                    WHERE tl.slug = $1 OR tl.id::text = $2
                    LIMIT 1
                """, webhook.tracking_id, webhook.affiliate_id)

                if not tracking_link:
                    # Log but don't fail - might be external affiliate
                    logger.warning(f"No tracking link found for webhook: {webhook.event_id}")
                    return {
                        "status": "accepted",
                        "message": "No matching tracking link",
                        "webhook_event_id": str(result['webhook_event_id'])
                    }

                # Create conversion
                conversion_id = await conn.fetchval("""
                    INSERT INTO conversions (
                        tracking_link_id,
                        order_id,
                        order_amount,
                        commission_amount,
                        status,
                        converted_at
                    ) VALUES ($1, $2, $3, $4, 'pending', NOW())
                    RETURNING id
                """,
                    tracking_link['id'],
                    webhook.order_id,
                    webhook.sale_amount,
                    webhook.commission_amount
                )

                # Create commission record
                platform_fee = webhook.commission_amount * Decimal("0.20")
                net_amount = webhook.commission_amount - platform_fee

                await conn.execute("""
                    INSERT INTO commissions (
                        influencer_id,
                        conversion_id,
                        amount,
                        platform_fee,
                        net_amount,
                        status
                    ) VALUES ($1, $2, $3, $4, $5, 'pending')
                """,
                    tracking_link['influencer_id'],
                    conversion_id,
                    webhook.commission_amount,
                    platform_fee,
                    net_amount
                )

                # Update webhook event with conversion_id
                await conn.execute("""
                    UPDATE webhook_events
                    SET conversion_id = $1
                    WHERE id = $2
                """, conversion_id, result['webhook_event_id'])

                # Update tracking link stats
                await conn.execute("""
                    UPDATE tracking_links
                    SET total_conversions = total_conversions + 1,
                        total_revenue = total_revenue + $2
                    WHERE id = $1
                """, tracking_link['id'], webhook.sale_amount)

                logger.info(f"Processed webhook {webhook.event_id}: conversion {conversion_id}")

                # Broadcast successful webhook and conversion
                await manager.broadcast_webhook(
                    source="refersion",
                    event_type=webhook.event_type,
                    status="processed",
                    event_id=webhook.event_id
                )

                await manager.broadcast_conversion(
                    order_id=webhook.order_id,
                    amount=float(webhook.sale_amount),
                    commission=float(webhook.commission_amount),
                    influencer_id=tracking_link['influencer_id']
                )

                return {
                    "status": "success",
                    "message": "Webhook processed successfully",
                    "webhook_event_id": str(result['webhook_event_id']),
                    "conversion_id": str(conversion_id)
                }

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            # Log error in webhook_events
            if 'webhook_event_id' in locals():
                await conn.execute("""
                    UPDATE webhook_events
                    SET status_code = 500,
                        error_message = $1
                    WHERE id = $2
                """, str(e), result['webhook_event_id'])
            raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/refersion/signature-info")
async def get_signature_info():
    """Get webhook signature configuration info"""
    import hashlib

    # Generate example signature for documentation
    example_payload = b'{"event_type":"sale","order_id":"123"}'
    example_signature = validator.compute_signature(example_payload)

    return {
        "signature_header": "X-Refersion-Signature",
        "signature_format": "sha256=<signature>",
        "algorithm": "sha256",
        "example": {
            "payload": example_payload.decode(),
            "signature": f"sha256={example_signature}",
            "description": "Include the X-Refersion-Signature header with this format"
        },
        "validation_enabled": os.getenv("ENVIRONMENT", "development") == "production",
        "webhook_secret_configured": webhook_secret != "dev_secret_change_in_production",
        "instructions": [
            "1. Set REFERSION_WEBHOOK_SECRET environment variable",
            "2. Configure Refersion to send signature header",
            "3. Use sha256 HMAC with the shared secret",
            "4. Include signature in X-Refersion-Signature header"
        ]
    }

@router.get("/refersion/test-idempotency")
async def test_idempotency_info():
    """Returns test instructions for webhook idempotency"""
    return {
        "instructions": "Send identical webhooks with same event_id to test idempotency",
        "expected_behavior": {
            "first_request": "201 Created with conversion_id",
            "duplicate_request": "202 Accepted without creating new conversion"
        },
        "curl_example": """
        # First request (creates conversion)
        curl -X POST http://localhost:8000/webhooks/refersion \\
          -H "Content-Type: application/json" \\
          -d '{
            "event_type": "sale",
            "event_id": "ref_evt_123456",
            "order_id": "ORDER_TEST_001",
            "affiliate_id": "aff_123",
            "commission_amount": 15.00,
            "sale_amount": 75.00,
            "tracking_id": "YOyqC7"
          }'

        # Second request (same event_id - returns 202)
        curl -X POST http://localhost:8000/webhooks/refersion \\
          -H "Content-Type: application/json" \\
          -d '{
            "event_type": "sale",
            "event_id": "ref_evt_123456",
            "order_id": "ORDER_TEST_001",
            "affiliate_id": "aff_123",
            "commission_amount": 15.00,
            "sale_amount": 75.00,
            "tracking_id": "YOyqC7"
          }'
        """
    }