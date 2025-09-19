# ADR-000: Tech Stack Decision

## Status
Accepted

## Context
SkinStack needs a reliable, scalable tech stack for building an influencer affiliate platform.

## Decision
We will use:
- **Framework**: FastAPI (Python)
- **Database**: Neon PostgreSQL (cloud-hosted)
- **Cache**: Redis
- **Testing**: pytest

## Rationale
- FastAPI: Async support, automatic OpenAPI docs, type hints
- Neon PostgreSQL: Serverless, auto-scaling, built-in pooling
- Redis: Fast caching and rate limiting
- pytest: Industry standard for Python testing

## Consequences
- ✅ Fast development with automatic API documentation
- ✅ Type safety with Pydantic
- ✅ Excellent async performance
- ❌ Team must know Python/FastAPI
- ❌ Less mature ecosystem than Node.js for some integrations

## Date
2025-01-17