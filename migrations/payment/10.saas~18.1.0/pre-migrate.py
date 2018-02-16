# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('payment.default_acquirer_button{,-todel}'))

    moved_views = util.splitlines("""
        pay_methods
        pay_meth_link
        pay
        confirm
    """)
    for view in moved_views:
        util.rename_xmlid(cr, 'website_payment.' + view, 'payment.' + view)
