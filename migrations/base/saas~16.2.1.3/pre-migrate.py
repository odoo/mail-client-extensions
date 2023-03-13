# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE res_users_apikeys DROP CONSTRAINT res_users_apikeys_user_id_fkey")
    cr.execute("ALTER TABLE res_users_apikeys ADD FOREIGN KEY (user_id) REFERENCES res_users(id) ON DELETE cascade")
