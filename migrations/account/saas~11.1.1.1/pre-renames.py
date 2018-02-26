# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('account.filter_invoice_{,report_}salespersons'))
    util.rename_xmlid(cr, *eb('account.access_account_invoice_{,line_}user'))
