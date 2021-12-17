# -*- coding: utf-8 -*-


def migrate(cr, version):

    cr.execute("ALTER TABLE res_users ALTER COLUMN helpdesk_target_closed TYPE int4")
