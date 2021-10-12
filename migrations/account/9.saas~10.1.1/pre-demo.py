# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # mark gone demo data as noupdate (cannot unlink non-draft invoices)
    util.force_noupdate(cr, "account.sale_of_land_line")
    util.force_noupdate(cr, "account.demo_invoice_invest_sale")
