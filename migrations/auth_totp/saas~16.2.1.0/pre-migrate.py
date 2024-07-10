def migrate(cr, version):
    cr.execute("ALTER TABLE auth_totp_device DROP CONSTRAINT IF EXISTS auth_totp_device_user_id_fkey")
    cr.execute("ALTER TABLE auth_totp_device ADD FOREIGN KEY (user_id) REFERENCES res_users(id) ON DELETE cascade")
