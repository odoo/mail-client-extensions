# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.team", "customer_satisfaction")
    cr.execute("ALTER TABLE res_users ALTER COLUMN helpdesk_target_closed TYPE int4")
