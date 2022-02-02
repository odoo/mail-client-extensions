# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if not util.version_gte("saas~15.2"):
        util.remove_field(cr, "hr.expense", "untaxed_amount")
