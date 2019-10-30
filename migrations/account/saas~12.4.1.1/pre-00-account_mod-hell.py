# -*- coding: utf-8 -*-
from odoo import models

# from odoo.addons.base.maintenance.migrations import util
from odoo.addons.account.models import account_move  # noqa


def migrate(cr, version):
    pass


class Move(models.Model):
    _inherit = "account.move"
    _module = "account"

    def _check_duplicate_supplier_reference(self):
        # Allow duplicated supplier references
        # Some old databases (like odoo.com) and some localisstiona (CH, see
        # odoo/odoo@55e676474782d6217dc95d7f14abd2166ab251f6) needs to have duplicated references.
        pass


class MoveLine(models.Model):
    _inherit = "account.move.line"
    _module = "account"

    def _check_account_currency(self):
        pass

    def _check_constrains_account_id(self):
        # Allow usage of deprecated accounts (during upgrade process)
        pass
