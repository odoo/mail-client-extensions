#!/usr/bin/env python
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'website_portal.orders_followup', 'website_portal_sale.orders_followup')
    util.force_noupdate(cr, 'website_portal.details', False)    # for csrf
