# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "account_move", "l10n_it_einvoice_name"):
        it_edi_format_id = util.ref(cr, "l10n_it_edi.edi_fatturaPA")

        cr.execute(
            """
            INSERT INTO account_edi_document (edi_format_id, move_id, state, attachment_id)
            SELECT %s, move.id, 'sent', (array_agg(ir_attachment.id ORDER BY ir_attachment.id DESC))[1]
              FROM account_move move
              JOIN ir_attachment ON ir_attachment.res_id = move.id AND ir_attachment.name = move.l10n_it_einvoice_name
             WHERE move.state = 'posted'
               AND move.l10n_it_einvoice_name IS NOT NULL
               AND ir_attachment.res_model = 'account.move'
          GROUP BY move.id
            """,
            [it_edi_format_id],
        )
