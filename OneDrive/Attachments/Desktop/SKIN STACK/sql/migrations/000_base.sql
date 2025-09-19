-- Migration 000: Base Schema
-- Empty migration to establish migration baseline
-- All future migrations will build on this

-- Migration metadata (for tracking)
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_migrations (version, name) VALUES (0, 'base')
ON CONFLICT (version) DO NOTHING;