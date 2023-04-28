# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "account_accountant.digest_tip_account_accountant_0", False)
    util.force_noupdate(cr, "account_accountant.digest_tip_account_accountant_1", False)
    util.remove_model(cr, "account.reconciliation.widget")
    util.remove_menus(cr, [util.ref(cr, "account_accountant.menu_action_manual_reconciliation")])
    util.remove_record(cr, "account_accountant.action_manual_reconciliation")
