# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_users", "odoobot_state", "varchar")
    cr.execute("UPDATE res_users set odoobot_state='disabled' WHERE odoobot_state IS NULL")
