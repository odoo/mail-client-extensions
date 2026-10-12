-- For production:
-- CREATE DATABASE must be run as root (e.g. postgres).
-- This script must be run as a dedicated user (e.g. gmail_addin) which has
-- the rights to create and alter tables.
-- For development:
-- CREATE DATABASE as well as this script can be run as any superuser.
-- Example:
-- createdb odoo_gmail_addin
-- psql -f init_db.sql odoo_gmail_addin

CREATE TABLE IF NOT EXISTS enc_users_settings (
    id SERIAL PRIMARY KEY,

    -- hash(derived key), used to retrieve the user's settings
    key_hash bytea NOT NULL UNIQUE,
    CONSTRAINT users_settings_key_hash_length_check CHECK (octet_length(key_hash) = 32),

    enc_odoo_url bytea,
    enc_odoo_token bytea,
    enc_translations bytea,
    enc_translations_expire_at bytea,

    -- temporary value used during the Odoo authentication process
    enc_login_token bytea,
    login_token_expire_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS enc_email_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message_id_hash  bytea NOT NULL,
    enc_res_id  bytea NOT NULL,
    enc_res_model  bytea NOT NULL,
    -- not encrypted to clean in the CRON
    create_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES enc_users_settings(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS enc_email_logs_user_id_idx ON enc_email_logs(user_id);
