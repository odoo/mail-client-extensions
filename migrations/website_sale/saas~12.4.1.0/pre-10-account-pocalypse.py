# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column('account_move', 'website_id', 'int4')

    util.remove_view('website_sale.account_invoice_view_form')
