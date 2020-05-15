# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.journal", "l10n_ar_sequence_ids")
    util.remove_field(cr, "ir.sequence", "l10n_ar_letter")

    util.remove_view(cr, "l10n_ar.sequence_view")
    util.remove_view(cr, "l10n_ar.sequence_view_tree")
    util.remove_view(cr, "l10n_ar.view_sequence_search")
