# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "account_accountant.account_invoice_view_form_supplier")
    util.remove_view(cr, "account_accountant.account_invoice_view_form_customer")
