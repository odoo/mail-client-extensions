# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'account_sepa.view_company_form_inherited')
