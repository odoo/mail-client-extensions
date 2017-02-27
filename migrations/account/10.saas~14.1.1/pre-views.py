# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'account.external_layout_footer')
    util.remove_view(cr, 'account.view_tax_form_cash_basis_inherit')
