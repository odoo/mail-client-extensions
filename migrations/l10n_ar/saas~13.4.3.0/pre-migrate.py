# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.journal", "l10n_ar_sequence_ids")
    util.remove_field(cr, "ir.sequence", "l10n_ar_letter")
