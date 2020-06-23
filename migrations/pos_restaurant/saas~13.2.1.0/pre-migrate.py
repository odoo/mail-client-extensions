# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "pos_order", "multiprint_resume", "varchar")
    util.create_column(cr, "pos_order_line", "mp_dirty", "boolean")
