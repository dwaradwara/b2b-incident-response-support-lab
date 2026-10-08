CREATE TABLE IF NOT EXISTS provider_config (
    provider_id TEXT PRIMARY KEY,
    provider_name TEXT NOT NULL,
    callback_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    region TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO provider_config (
    provider_id,
    provider_name,
    callback_enabled,
    region
)
VALUES (
    'provider_demo_001',
    'Demo Gaming Provider',
    TRUE,
    'EU'
)
ON CONFLICT (provider_id) DO NOTHING;
