# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces

    xids = util.splitlines("""
        portal_account_invoice_user_rule
        portal_account_invoice_line_rule
        access_account_invoice
        access_account_invoice_line

        portal_my_home_menu_invoice
        portal_my_home_invoice
        portal_my_invoices

        view_account_invoice_filter_share
    """)

    for x in xids:
        util.rename_xmlid(cr, *eb('website_{portal_sale,account}.' + x))
