# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, 'res.company', 'dms_product_settings', 'documents_product_settings')
    util.rename_field(cr, 'res.config.settings', 'dms_product_settings', 'documents_product_settings')
