"""Webhook signature validation for security"""
import hmac
import hashlib
import time
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, Header
import json


class WebhookValidator:
    """
    Validates webhook signatures to ensure authenticity.
    Supports multiple signature schemes.
    """

    def __init__(self, secret_key: str):
        """
        Initialize with a secret key for signature validation.

        Args:
            secret_key: Shared secret key for HMAC validation
        """
        self.secret_key = secret_key.encode() if isinstance(secret_key, str) else secret_key

    def compute_signature(
        self,
        payload: bytes,
        timestamp: Optional[str] = None,
        algorithm: str = "sha256"
    ) -> str:
        """
        Compute HMAC signature for payload.

        Args:
            payload: Request body bytes
            timestamp: Optional timestamp for replay protection
            algorithm: Hash algorithm (sha256, sha512)

        Returns:
            Computed signature hex string
        """
        # Include timestamp in signature if provided
        if timestamp:
            signed_payload = f"{timestamp}.{payload.decode()}".encode()
        else:
            signed_payload = payload

        # Compute HMAC
        if algorithm == "sha256":
            signature = hmac.new(
                self.secret_key,
                signed_payload,
                hashlib.sha256
            ).hexdigest()
        elif algorithm == "sha512":
            signature = hmac.new(
                self.secret_key,
                signed_payload,
                hashlib.sha512
            ).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        return signature

    def validate_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: Optional[str] = None,
        algorithm: str = "sha256",
        max_age_seconds: int = 300  # 5 minutes
    ) -> bool:
        """
        Validate webhook signature.

        Args:
            payload: Request body bytes
            signature: Signature to validate
            timestamp: Optional timestamp for replay protection
            algorithm: Hash algorithm used
            max_age_seconds: Maximum age for timestamp validation

        Returns:
            True if signature is valid, False otherwise
        """
        # Check timestamp age if provided
        if timestamp:
            try:
                timestamp_int = int(timestamp)
                current_time = int(time.time())

                # Check if timestamp is too old
                if current_time - timestamp_int > max_age_seconds:
                    return False

                # Check if timestamp is in the future (clock skew tolerance)
                if timestamp_int - current_time > 60:  # 1 minute tolerance
                    return False

            except (ValueError, TypeError):
                return False

        # Compute expected signature
        expected_signature = self.compute_signature(payload, timestamp, algorithm)

        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(signature, expected_signature)

    async def validate_refersion_webhook(
        self,
        request: Request,
        x_refersion_signature: Optional[str] = Header(None)
    ) -> Dict[str, Any]:
        """
        Validate Refersion webhook signature.

        Refersion sends signature in X-Refersion-Signature header.
        Format: sha256=<signature>

        Args:
            request: FastAPI request object
            x_refersion_signature: Signature header

        Returns:
            Validated webhook data

        Raises:
            HTTPException: If signature is invalid
        """
        # Get request body
        body = await request.body()

        # Check if signature header is present
        if not x_refersion_signature:
            # In development, allow unsigned webhooks with warning
            if hasattr(request.app.state, 'settings') and \
               request.app.state.settings.environment == "development":
                print("[WARN] Webhook received without signature (dev mode)")
                return json.loads(body)

            raise HTTPException(
                status_code=401,
                detail="Missing webhook signature"
            )

        # Parse signature header (format: sha256=<signature>)
        try:
            algorithm, signature = x_refersion_signature.split("=", 1)
            if algorithm not in ["sha256", "sha512"]:
                raise ValueError("Invalid algorithm")
        except ValueError:
            raise HTTPException(
                status_code=401,
                detail="Invalid signature format"
            )

        # Validate signature
        if not self.validate_signature(body, signature, algorithm=algorithm):
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature"
            )

        # Parse and return validated data
        return json.loads(body)

    async def validate_stripe_webhook(
        self,
        request: Request,
        stripe_signature: Optional[str] = Header(None)
    ) -> Dict[str, Any]:
        """
        Validate Stripe webhook signature.

        Stripe sends signature in Stripe-Signature header.
        Format: t=<timestamp>,v1=<signature>,v0=<legacy_signature>

        Args:
            request: FastAPI request object
            stripe_signature: Stripe signature header

        Returns:
            Validated webhook data

        Raises:
            HTTPException: If signature is invalid
        """
        # Get request body
        body = await request.body()

        # Check if signature header is present
        if not stripe_signature:
            raise HTTPException(
                status_code=401,
                detail="Missing Stripe signature"
            )

        # Parse Stripe signature header
        elements = {}
        for element in stripe_signature.split(","):
            key, value = element.split("=", 1)
            elements[key] = value

        # Get timestamp and signature
        timestamp = elements.get("t")
        signature = elements.get("v1")  # v1 is current version

        if not timestamp or not signature:
            raise HTTPException(
                status_code=401,
                detail="Invalid Stripe signature format"
            )

        # Validate signature with timestamp
        if not self.validate_signature(
            body,
            signature,
            timestamp=timestamp,
            algorithm="sha256"
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid Stripe webhook signature"
            )

        # Parse and return validated data
        return json.loads(body)

    async def validate_generic_webhook(
        self,
        request: Request,
        signature_header: str = "X-Webhook-Signature",
        timestamp_header: str = "X-Webhook-Timestamp",
        algorithm: str = "sha256"
    ) -> Dict[str, Any]:
        """
        Validate generic webhook with configurable headers.

        Args:
            request: FastAPI request object
            signature_header: Name of signature header
            timestamp_header: Name of timestamp header
            algorithm: Hash algorithm to use

        Returns:
            Validated webhook data

        Raises:
            HTTPException: If signature is invalid
        """
        # Get request body
        body = await request.body()

        # Get headers
        signature = request.headers.get(signature_header)
        timestamp = request.headers.get(timestamp_header)

        # Check if signature is present
        if not signature:
            # In development, allow unsigned webhooks
            if hasattr(request.app.state, 'settings') and \
               request.app.state.settings.environment == "development":
                print(f"[WARN] Webhook without signature (dev mode)")
                return json.loads(body)

            raise HTTPException(
                status_code=401,
                detail=f"Missing {signature_header} header"
            )

        # Validate signature
        if not self.validate_signature(
            body,
            signature,
            timestamp=timestamp,
            algorithm=algorithm
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature"
            )

        # Parse and return validated data
        return json.loads(body)


def create_webhook_secret(provider: str) -> str:
    """
    Generate a secure webhook secret for a provider.

    Args:
        provider: Provider name (refersion, stripe, etc.)

    Returns:
        Secure random secret string
    """
    import secrets
    # Generate 32-byte secure random string
    secret = secrets.token_hex(32)
    return f"{provider}_{secret}"


# Example usage in settings
class WebhookSettings:
    """Webhook security settings"""

    def __init__(self):
        # Load from environment or generate
        import os
        self.refersion_secret = os.getenv(
            "REFERSION_WEBHOOK_SECRET",
            "dev_secret_change_in_production"
        )
        self.stripe_secret = os.getenv(
            "STRIPE_WEBHOOK_SECRET",
            "dev_secret_change_in_production"
        )
        self.generic_secret = os.getenv(
            "WEBHOOK_SECRET",
            "dev_secret_change_in_production"
        )

        # Create validators
        self.refersion_validator = WebhookValidator(self.refersion_secret)
        self.stripe_validator = WebhookValidator(self.stripe_secret)
        self.generic_validator = WebhookValidator(self.generic_secret)