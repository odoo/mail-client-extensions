# -*- coding: utf-8 -*-
from odoo import models
from odoo.addons.account.models import account_journal as _ignore  # noqa


def migrate(cr, version):
    pass


class Journal(models.Model):
    _inherit = "account.journal"
    _module = "account"

    def _check_journal_not_shared_accounts(self):
        pass


class Account(models.Model):
    _inherit = "account.account"
    _module = "account"

    def write(self, vals):
        vals.pop("currency_id", False)
        return super().write(vals)

    def _check_user_type_id_unique_current_year_earning(self):
        return True


class Move(models.Model):
    _inherit = "account.move"
    _module = "account"
    _check_company_auto = False

    def _check_unique_sequence_number(self):
        return True


class MoveLine(models.Model):
    _inherit = "account.move.line"
    _module = "account"
    _check_company_auto = False


class Payment(models.Model):
    _inherit = "account.payment"
    _module = "account"
    _check_company_auto = False
