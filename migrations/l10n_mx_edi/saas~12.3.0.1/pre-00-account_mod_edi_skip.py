# -*- coding: utf-8 -*-
from odoo import models

from odoo.addons.l10n_mx_edi.models import account_invoice  # noqa


def migrate(cr, version):
    pass


class AccountInvoice(models.Model):
    _inherit = "account.invoice"  # TODO: won't this crash in v13?
    _module = "l10n_mx_edi"

    def l10n_mx_edi_is_required(self):
        return False


class Move(models.Model):
    _inherit = "account.move"
    _module = "l10n_mx_edi"

    def l10n_mx_edi_is_required(self):
        return False
