# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    names = util.splitlines("""
        repair_fee
        repair
        product_pricelist
        stock_production_lot
        repair_line
        account_tax
        account_invoice
        account_invoice_line
        account_journal
    """)
    for name in names:
        util.remove_record(cr, "repair.access_%s_manager" % name)

    util.remove_record(cr, "repair.access_repair_fee_user_mrp")
    util.remove_record(cr, "repair.access_repair_fee_mgr")
