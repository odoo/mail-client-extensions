# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.modules_auto_discovery(cr, force_upgrades={"appointment_sms"})

    if util.has_enterprise():
        util.merge_module(cr, "documents_spreadsheet_bundle", "documents_spreadsheet")
        util.merge_module(cr, "sale_amazon_spapi", "sale_amazon")

    util.remove_module(cr, 'account_accountant_check_printing')
