# -*- coding: utf-8 -*-
from odoo import models

from odoo.addons.account.models import account_journal as _ignore  # noqa

from odoo.addons.base.maintenance.migrations import util


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


class SequenceMixin(models.AbstractModel):
    _inherit = "sequence.mixin"
    _module = "account"

    def _constrains_date_sequence(self):
        return True


class Move(models.Model):
    _inherit = "account.move"
    _module = "account"
    _check_company_auto = False

    def _check_unique_sequence_number(self):
        return True

    def _get_invoice_in_payment_state(self):
        # The code changing the bank account to the oustanding account on payments in on the 'account' module.
        # When setting the account, _compute_amount is called on the invoices but since `account_accountant` is not yet loaded,
        # the 'in_payment' state isn't set correctly.
        return "in_payment" if util.ENVIRON["account_accountant_installed"] else "paid"


class MoveLine(models.Model):
    _inherit = "account.move.line"
    _module = "account"
    _check_company_auto = False

    def _check_constrains_account_id_journal_id(self):
        return True


class Payment(models.Model):
    _inherit = "account.payment"
    _module = "account"
    _check_company_auto = False


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    _module = "account"
    _check_company_auto = False
