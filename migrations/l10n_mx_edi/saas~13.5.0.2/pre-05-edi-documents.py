# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # migrate to the new edi api.
    util.update_record_from_xml(cr, "l10n_mx_edi.edi_cfdi_3_3", force_create=True)
    mx_edi_format_id = util.ref(cr, "l10n_mx_edi.edi_cfdi_3_3")

    # Posted/signed invoices.
    cr.execute(
        """
        WITH cfdi_per_move AS (
            SELECT
                move.id AS move_id,
                attachment.id AS attachment_id,
                ROW_NUMBER() OVER(PARTITION BY move.id ORDER BY attachment.create_date DESC, attachment.id DESC) AS rank
            FROM account_move move
            JOIN ir_attachment attachment ON
                attachment.name = move.l10n_mx_edi_cfdi_name
                AND
                attachment.res_model = 'account.move'
                AND
                attachment.res_id = move.id
                AND
                attachment.company_id = move.company_id
            WHERE move.l10n_mx_edi_pac_status = 'signed'
            AND move.state = 'posted'
        )
        INSERT INTO account_edi_document (edi_format_id, move_id, state, attachment_id)
        SELECT
            %s,
            cfdi_per_move.move_id,
            'sent',
            cfdi_per_move.attachment_id
        FROM cfdi_per_move
        WHERE cfdi_per_move.rank = 1
        """,
        [mx_edi_format_id],
    )

    # Posted/not signed invoices.
    cr.execute(
        """
        INSERT INTO account_edi_document (edi_format_id, move_id, state)
        SELECT
            %s,
            account_move.id,
            'to_send'
        FROM account_move
        WHERE account_move.l10n_mx_edi_pac_status IN ('retry', 'to_sign')
        AND account_move.state = 'posted'
        """,
        [mx_edi_format_id],
    )

    # Link from payments
    cr.execute(
        """
        WITH cfdi_per_payment AS (
            SELECT
                move.id AS move_id,
                attachment.id AS attachment_id,
                ROW_NUMBER() OVER(PARTITION BY pay.id ORDER BY attachment.create_date DESC, attachment.id DESC) AS rank
            FROM account_payment pay
            JOIN ir_attachment attachment ON
                attachment.res_model = 'account.payment'
                AND
                attachment.res_id = pay.id
            JOIN account_move move ON
                pay.move_id = move.id
                AND
                attachment.company_id = move.company_id
           WHERE move.state = 'posted'
        )
        INSERT INTO account_edi_document (edi_format_id, move_id, state, attachment_id)
        SELECT
            %s,
            cfdi_per_payment.move_id,
            'sent',
            cfdi_per_payment.attachment_id
        FROM cfdi_per_payment
        WHERE cfdi_per_payment.rank = 1
        """,
        [mx_edi_format_id],
    )
