# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_cl.sequence_view")
    util.remove_view(cr, "l10n_cl.view_sequence_search")

    util.remove_field(cr, "account.journal", "l10n_cl_sequence_ids")
    util.remove_field(cr, "ir.sequence", "l10n_cl_journal_ids")
