CREATE DATABASE odoo_gmail_addin_db;

\c odoo_gmail_addin_db;

CREATE TABLE users_settings (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    odoo_url TEXT,
    odoo_token TEXT,
    login_token TEXT,
    login_token_expire_at TIMESTAMP WITH TIME ZONE,
    translations JSON,
    translations_expire_at TIMESTAMP WITH TIME ZONE
);

-- Remember that the user logged the email on the giver record
CREATE TABLE email_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message_id TEXT NOT NULL,
    res_id INTEGER NOT NULL,
    res_model TEXT NOT NULL,
    create_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users_settings(id) ON DELETE CASCADE
);
