#!/bin/bash

# Webhook Idempotency Test Examples
# Expected behavior:
#   - First request: 200 OK with conversion_id
#   - Duplicate request: 202 Accepted without new conversion

echo "=========================================="
echo "WEBHOOK IDEMPOTENCY TEST"
echo "=========================================="

# Test webhook endpoint
URL="http://localhost:8000/webhooks/refersion"

# Use timestamp to ensure unique event_id across test runs
TIMESTAMP=$(date +%s)
EVENT_ID="ref_evt_${TIMESTAMP}"

echo ""
echo "[1] First request (should create conversion - 200 OK):"
echo "----------------------------------------------"

curl -X POST $URL \
  -H "Content-Type: application/json" \
  -d "{
    \"event_type\": \"sale\",
    \"event_id\": \"${EVENT_ID}\",
    \"order_id\": \"ORDER_${TIMESTAMP}\",
    \"affiliate_id\": \"aff_123\",
    \"commission_amount\": 15.00,
    \"sale_amount\": 75.00,
    \"tracking_id\": \"YOyqC7\"
  }" \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo ""
echo "[2] Duplicate request (same event_id - should return 202 Accepted):"
echo "----------------------------------------------"

curl -X POST $URL \
  -H "Content-Type: application/json" \
  -d "{
    \"event_type\": \"sale\",
    \"event_id\": \"${EVENT_ID}\",
    \"order_id\": \"ORDER_${TIMESTAMP}\",
    \"affiliate_id\": \"aff_123\",
    \"commission_amount\": 15.00,
    \"sale_amount\": 75.00,
    \"tracking_id\": \"YOyqC7\"
  }" \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo ""
echo "[3] Different event_id (should create new conversion - 200 OK):"
echo "----------------------------------------------"

NEW_EVENT_ID="ref_evt_${TIMESTAMP}_new"

curl -X POST $URL \
  -H "Content-Type: application/json" \
  -d "{
    \"event_type\": \"sale\",
    \"event_id\": \"${NEW_EVENT_ID}\",
    \"order_id\": \"ORDER_${TIMESTAMP}_NEW\",
    \"affiliate_id\": \"aff_456\",
    \"commission_amount\": 20.00,
    \"sale_amount\": 100.00,
    \"tracking_id\": \"YOyqC7\"
  }" \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
echo ""
echo "Expected results:"
echo "  1. First request: 200 OK with conversion_id"
echo "  2. Duplicate: 202 Accepted (no new conversion)"
echo "  3. Different ID: 200 OK with new conversion_id"