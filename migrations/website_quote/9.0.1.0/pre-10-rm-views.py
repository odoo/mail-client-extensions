# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    views = util.splitlines("""
        assets_frontend
        pricing
        chatter
        so_quotation
        so_quotation_content
        quotations
    """)
    for v in views:
        util.force_noupdate(cr, 'website_quote.' + v, False)
