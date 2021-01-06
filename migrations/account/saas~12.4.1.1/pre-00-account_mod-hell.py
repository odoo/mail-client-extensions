# -*- coding: utf-8 -*-
import os
from odoo import models
from odoo.tools.misc import str2bool

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


if str2bool(os.getenv("MATT", "0")):
    # Some l10n_ modules create invoice demo data
    # While these records are in noupdate, to determine their existance, the ORM try loading them.
    # However, as their xmlid still point to the `account.invoice` model (because the records are only converted in `end-` script),
    # it crash because the model doesn't exists (actually, it just log a warning with the traceback and the failed demo xml file).
    # Avoid it by creating a minimal `account.invoice` model. It will works because the ORM, only read the record id.

    class Invoice(models.Model):
        _name = "account.invoice"
        _module = "account"
        _description = "Not the `account.invoice` you are looking for..."
