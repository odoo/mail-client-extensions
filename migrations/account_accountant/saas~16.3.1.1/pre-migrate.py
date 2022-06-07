# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "account_accountant.digest_tip_account_accountant_0", False)
    util.force_noupdate(cr, "account_accountant.digest_tip_account_accountant_1", False)
