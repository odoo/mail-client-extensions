# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "pos_config", "module_pos_loyalty", "boolean")
    cr.execute("UPDATE pos_config SET module_pos_loyalty = (loyalty_id IS NOT NULL)")

    util.create_column(cr, "loyalty_program", "active", "boolean", default=True)
