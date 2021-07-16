# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    util.update_record_from_xml(cr, "l10n_co_edi.edi_carvajal", force_create=True)
    co_edi_format_id = util.ref(cr, "l10n_co_edi.edi_carvajal")

    # Posted/not signed, processing invoices
    cr.execute(
        """
        INSERT INTO account_edi_document (edi_format_id, move_id, state)
        SELECT %s, id, 'to_send'
          FROM account_move
         WHERE l10n_co_edi_invoice_status IN ('not_sent', 'processing')
           AND state = 'posted'
    """,
        [co_edi_format_id],
    )

    # Posted/signed invoices.
    cr.execute(
        """
        WITH carvajal_move AS (
           SELECT
                move.id AS move_id,
                a.id AS attachment_id,
                ROW_NUMBER() OVER(PARTITION BY move.id ORDER BY a.create_date DESC, a.id DESC) AS rank
             FROM account_move move
             JOIN ir_attachment a ON (a.res_model = 'account.move' AND a.res_id = move.id)
            WHERE move.l10n_co_edi_invoice_status = 'accepted'
              AND a.name = move.l10n_co_edi_invoice_name
              AND a.company_id = move.company_id
              AND move.state = 'posted'
        )
        INSERT INTO account_edi_document (edi_format_id, move_id, state, attachment_id)
             SELECT %s, move_id, 'sent', attachment_id
               FROM carvajal_move
              WHERE rank = 1
    """,
        [co_edi_format_id],
    )

    # Posted/rejected
    cr.execute(
        """
        INSERT INTO account_edi_document (edi_format_id, move_id, state, error, blocking_level)
             SELECT %s, account_move.id, 'to_send', 'The invoice was rejected by Carvajal', 'error'
               FROM account_move
              WHERE account_move.l10n_co_edi_invoice_status = 'rejected'
                AND account_move.state = 'posted'
    """,
        [co_edi_format_id],
    )

    # Obligation types
    default_obligation_type = util.ref(cr, "l10n_co_edi.obligation_type_5")
    cr.execute(
        """
        UPDATE partner_l10n_co_edi_obligation_types p
           SET type_id = %s
          FROM l10n_co_edi_type_code t
         WHERE p.type_id = t.id AND t.name NOT IN ('O-47', 'R-99-PN', 'O-13', 'O-15', 'O-23')
    """,
        [default_obligation_type],
    )

    # Cleanup
    util.remove_view(cr, "l10n_co_edi.view_country_state_form_inherit_l10n_co_edi")
    util.remove_record(cr, "l10n_co_edi.upload_electronic_invoice_server_action")
    util.remove_record(cr, "l10n_co_edi.check_status_electronic_invoice_server_action")

    util.remove_field(cr, "account.move", "l10n_co_edi_invoice_status")
    util.remove_field(cr, "account.move", "l10n_co_edi_invoice_name")
    util.remove_field(cr, "account.move", "l10n_co_edi_datetime_invoice")
    util.remove_field(cr, "res.partner", "l10n_co_edi_simplified_regimen")
    util.remove_field(cr, "res.partner", "l10n_co_edi_representation_type_id")
    util.remove_field(cr, "res.partner", "l10n_co_edi_establishment_type_id")
    util.remove_field(cr, "res.partner", "l10n_co_edi_customs_type_ids")
    cr.execute("DROP TABLE IF EXISTS partner_l10n_co_edi_customs_types")
    util.remove_field(cr, "l10n_co_edi.type_code", "type")
