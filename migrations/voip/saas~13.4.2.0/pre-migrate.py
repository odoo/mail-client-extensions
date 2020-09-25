# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # While the default for new users is to ask, for current users, use `voip` to keep previous behavior
    util.create_column(cr, "res_users", "mobile_call_method", "varchar", default="voip")
