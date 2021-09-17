# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "consolidation_group", "invert_sign", "boolean")
    util.create_column(cr, "consolidation_account", "invert_sign", "boolean")
    util.create_column(cr, "consolidation_chart", "invert_sign", "boolean")
