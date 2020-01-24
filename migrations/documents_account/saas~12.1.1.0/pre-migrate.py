# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("documents.documents_replace_{inbox,documents}_vendor_bill"))
    util.rename_field(cr, 'res.company', 'dms_account_settings', 'documents_account_settings')
    util.rename_field(cr, 'res.config.settings', 'dms_account_settings', 'documents_account_settings')
