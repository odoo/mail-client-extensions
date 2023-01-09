# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_tax
           SET l10n_mx_tax_type = l10n_mx_cfdi_tax_type
         WHERE l10n_mx_cfdi_tax_type IS NOT NULL
        """
    )
    util.remove_field(cr, "account.tax", "l10n_mx_cfdi_tax_type")

    util.create_column(cr, "account_move", "l10n_mx_edi_cfdi_request", "varchar")
    util.create_column(cr, "account_move", "l10n_mx_edi_post_time", "timestamp without time zone")

    updates = [
        """
            UPDATE account_move m
               SET l10n_mx_edi_cfdi_request = CASE
                        WHEN m.payment_id IS NOT NULL OR m.statement_line_id IS NOT NULL
                        THEN 'on_payment'
                        WHEN m.move_type = 'out_invoice' THEN 'on_invoice'
                        WHEN m.move_type = 'out_refund' THEN 'on_refund'
                   END
              FROM res_company c
              JOIN res_partner p ON p.id = c.partner_id
              JOIN res_country k ON k.id = p.country_id
             WHERE c.id = m.company_id
               AND upper(k.code) = 'MX'
        """,
        """
            UPDATE account_move m
               SET partner_bank_id = l10n_mx_edi_partner_bank_id
             WHERE l10n_mx_edi_cfdi_request IN ('on_invoice', 'on_refund')
        """,
        """
            UPDATE account_move m
               SET l10n_mx_edi_payment_method_id = p.l10n_mx_edi_payment_method_id,
                   l10n_mx_edi_pac_status = p.l10n_mx_edi_pac_status,
                   l10n_mx_edi_sat_status = p.l10n_mx_edi_sat_status,
                   l10n_mx_edi_origin = p.l10n_mx_edi_origin,
                   partner_bank_id = p.l10n_mx_edi_partner_bank_id,
                   l10n_mx_edi_time_invoice = p.l10n_mx_edi_time_payment
             FROM account_payment p
            WHERE m.payment_id = p.id
        """,
        """
            UPDATE account_move m
               SET l10n_mx_edi_payment_method_id = l.l10n_mx_edi_payment_method_id
              FROM account_bank_statement_line l
             WHERE m.id = l.move_id
        """,
    ]
    for query in updates:
        util.parallel_execute(cr, util.explode_query(cr, query, alias="m"))

    # Migrate 'l10n_mx_edi_time_invoice' (char) to 'l10n_mx_edi_post_time' (datetime)
    cr.execute(
        """
        WITH cfdi_per_move AS (
            SELECT
                move.id AS move_id,
                attachment.create_date AS date,
                ROW_NUMBER() OVER(PARTITION BY move.id ORDER BY attachment.create_date DESC) AS rank
            FROM account_move move
            JOIN ir_attachment attachment ON attachment.name = move.l10n_mx_edi_cfdi_name
            WHERE move.state = 'posted'
        )
        UPDATE account_move move
        SET l10n_mx_edi_post_time =
                (LEFT(cfdi_per_move.date::varchar, 10) || ' ' || move.l10n_mx_edi_time_invoice || '.000000')::timestamp
        FROM cfdi_per_move
        WHERE cfdi_per_move.move_id = move.id
        AND cfdi_per_move.rank = 1
        AND LENGTH(move.l10n_mx_edi_time_invoice) = 8
    """
    )

    #
    util.remove_model(cr, "l10n_mx_edi.pac.sw.mixin")
    util.remove_field(cr, "account.payment.register", "l10n_mx_edi_partner_bank_id")
    #
    # move models to new module `l10n_mx_edi_extended`
    util.move_model(cr, "l10n_mx_edi.res.locality", "l10n_mx_edi", "l10n_mx_edi_extended", move_data=True)
    util.move_model(cr, "l10n_mx_edi.tariff.fraction", "l10n_mx_edi", "l10n_mx_edi_extended", move_data=True)

    # move fields to new module `l10n_mx_edi_extended`
    p = "l10n_mx_edi_"  # common prefix
    move_fields = {
        "account.journal": ("l10n_mx_address_issued_id",),
        "account.move": (f"{p}external_trade",),
        "account.move.line": (f"{p}customs_number", f"{p}umt_aduana_id", f"{p}qty_umt", f"{p}price_unit_umt"),
        "product.template": (f"{p}tariff_fraction_id", f"{p}umt_aduana_id"),
        "res.company": (f"{p}locality", f"{p}locality_id", f"{p}num_exporter"),
        "res.config.settings": (f"{p}num_exporter",),
        "uom.uom": (f"{p}code_aduana",),
        "res.partner": (f"{p}locality", f"{p}locality_id", f"{p}curp", f"{p}external_trade"),
    }

    for model, fields in move_fields.items():
        for field in fields:
            util.move_field_to_module(cr, model, field, "l10n_mx_edi", "l10n_mx_edi_extended")

    # Cleanup fields
    util.remove_field(cr, "account.bank.statement.line", "l10n_mx_edi_payment_method_id")

    util.remove_field(cr, "account.payment", "l10n_mx_edi_pac_status")
    util.remove_field(cr, "account.payment", "l10n_mx_edi_sat_status")
    util.remove_field(cr, "account.payment", "l10n_mx_edi_payment_method_id")
    util.remove_field(cr, "account.payment", "l10n_mx_edi_origin")
    util.remove_field(cr, "account.payment", "l10n_mx_edi_cfdi")
    util.remove_field(cr, "account.payment", "l10n_mx_edi_expedition_date")
    util.remove_field(cr, "account.payment", "l10n_mx_edi_time_payment")
    util.remove_field(cr, "account.payment", "l10n_mx_edi_partner_bank_id")
    util.remove_field(cr, "account.payment", "l10n_mx_edi_cfdi_name")

    util.remove_field(cr, "account.move", "l10n_mx_edi_cfdi_name")
    util.remove_field(cr, "account.move", "l10n_mx_edi_partner_bank_id")
    util.remove_field(cr, "account.move", "l10n_mx_edi_cfdi")
    util.remove_field(cr, "account.move", "l10n_mx_edi_time_invoice")
    util.remove_field(cr, "account.move", "l10n_mx_edi_pac_status")
    util.remove_field(cr, "account.move.line", "l10n_mx_edi_tariff_fraction_id")

    # clean data
    util.remove_record(cr, "l10n_mx_edi.update_pac_status_server_action")
    util.remove_record(cr, "l10n_mx_edi.l10n_mx_edi_xsd_server_action")
    util.remove_record(cr, "l10n_mx_edi.l10n_mx_edi_revert_cancellation")

    util.remove_record(cr, "l10n_mx_edi.ir_cron_cancellation_invoices_open_to_cancel")
    util.remove_record(cr, "l10n_mx_edi.ir_cron_cancellation_invoices_cancel_signed_sat")
    util.remove_record(cr, "l10n_mx_edi.ir_cron_update_state_invoice")
    util.remove_record(cr, "l10n_mx_edi.ir_cron_update_state_payment")

    util.remove_record(cr, "l10n_mx_edi.res_partner_category_force_rep")
    util.remove_record(cr, "l10n_mx_edi.l10n_mx_edi_version_cfdi")

    util.remove_view(cr, "l10n_mx_edi.res_partner_form_inherit_l10n_mx_edi")
    util.remove_view(cr, "l10n_mx_edi.view_l10n_mx_edi_invoice_filter_inherit")
    util.remove_view(cr, "l10n_mx_edi.external_tradev11")

    util.rename_xmlid(
        cr, *util.expand_braces("{l10n_mx_edi,l10n_mx_edi_extended}.l10n_mx_edi_tariff_fraction_tree_view")
    )
    util.rename_xmlid(cr, *util.expand_braces("{l10n_mx_edi,l10n_mx_edi_extended}.view_product_uom_form_inh_l10n_mx"))
    util.rename_xmlid(cr, *util.expand_braces("{l10n_mx_edi,l10n_mx_edi_extended}.view_prod_form_inh_l10n_mx"))
