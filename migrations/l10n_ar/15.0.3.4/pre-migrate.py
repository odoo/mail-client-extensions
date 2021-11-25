# -*- coding: utf-8 -*-
from odoo import fields, models


def migrate(cr, version):
    pass


class Reversal(models.TransientModel):
    _inherit = "account.move.reversal"
    _module = "l10n_ar"

    # The module creates reversal moves (demo data) through this wizard.
    # As we are in update mode, the <function> tags won't be called.
    # So we don't care about inconsistent data
    journal_id = fields.Many2one(check_company=False)
