# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE res_company ALTER COLUMN gengo_private_key TYPE VARCHAR")
