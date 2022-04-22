# -*- coding: utf-8 -*-
from odoo import models

from odoo.addons.l10n_au_aba.models import account_payment  # noqa


class AccountPayment(models.Model):
    _inherit = "account.payment"
    _module = "l10n_au_aba"

    def _check_partner_bank_account(self):
        if all(p.state in {"draft", "cancelled"} for p in self):
            return True
        return super()._check_partner_bank_account()
