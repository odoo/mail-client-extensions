# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'website_quote.opt_quotation_signature')
    util.remove_view(cr, 'website_quote.quotations')
