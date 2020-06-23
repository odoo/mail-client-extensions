# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "l10n_latam_sequence_id")
    util.remove_field(cr, "account.move", "l10n_latam_document_number")

    util.remove_column(cr, "account_move_reversal", "l10n_latam_use_documents")
    util.remove_column(cr, "account_move_reversal", "l10n_latam_document_type_id")
    util.remove_field(cr, "account.move.reversal", "l10n_latam_sequence_id")
