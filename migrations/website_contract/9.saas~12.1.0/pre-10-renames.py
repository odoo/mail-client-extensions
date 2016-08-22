# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'website_contract.contracts', 'website_contract.portal_my_contracts')
