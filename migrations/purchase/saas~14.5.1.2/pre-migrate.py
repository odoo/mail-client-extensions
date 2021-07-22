# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===============================================================
    # Withholding taxes (Task 2457374 - PR 74138)
    # ===============================================================
    util.remove_field(cr, "purchase.order", "amount_by_group")
