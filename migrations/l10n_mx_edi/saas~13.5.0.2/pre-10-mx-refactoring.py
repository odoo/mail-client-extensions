# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    # ===========================================================
    # account_edi + refactoring l10n_mx_edi (PR: 52407 & 12226)
    # ===========================================================

    # Cleanup records.

    util.remove_record(cr, 'l10n_mx_edi.update_pac_status_server_action')
    util.remove_record(cr, 'l10n_mx_edi.l10n_mx_edi_xsd_server_action')
    util.remove_record(cr, 'l10n_mx_edi.l10n_mx_edi_revert_cancellation')
    util.remove_record(cr, 'l10n_mx_edi.ir_cron_cancellation_invoices_open_to_cancel')
    util.remove_record(cr, 'l10n_mx_edi.ir_cron_cancellation_invoices_cancel_signed_sat')
    util.remove_record(cr, 'l10n_mx_edi.ir_cron_update_state_invoice')
    util.remove_record(cr, 'l10n_mx_edi.ir_cron_update_state_payment')
    util.remove_record(cr, 'l10n_mx_edi.ir_cron_download_xsd_files')
    util.remove_record(cr, 'l10n_mx_edi.res_partner_category_force_rep')
    util.remove_record(cr, 'l10n_mx_edi.l10n_mx_edi_version_cfdi')
    util.remove_record(cr, 'l10n_mx_edi.view_l10n_mx_edi_invoice_filter_inherit')
    util.remove_record(cr, 'l10n_mx_edi.external_tradev11')
    util.rename_xmlid(cr, *util.expand_braces('{l10n_mx_edi,l10n_mx_edi_extended}.l10n_mx_edi_tariff_fraction_tree_view'))
    util.rename_xmlid(cr, *util.expand_braces('{l10n_mx_edi,l10n_mx_edi_extended}.view_product_uom_form_inh_l10n_mx'))
    util.rename_xmlid(cr, *util.expand_braces('{l10n_mx_edi,l10n_mx_edi_extended}.view_prod_form_inh_l10n_mx'))

    # account.tax

    cr.execute('''
        UPDATE account_tax
        SET l10n_mx_tax_type = l10n_mx_cfdi_tax_type
        WHERE l10n_mx_cfdi_tax_type IS NOT NULL
    ''')

    util.remove_field(cr, 'account.tax', 'l10n_mx_cfdi_tax_type')

    # account.journal

    util.move_field_to_module(cr, 'account.journal', 'l10n_mx_address_issued_id', 'l10n_mx_edi', 'l10n_mx_edi_extended')

    # account.move

    util.create_column(cr, 'account_move', 'l10n_mx_edi_cfdi_request', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_mx_edi_post_time', 'timestamp without time zone')

    util.move_field_to_module(cr, 'account.move', 'l10n_mx_edi_external_trade', 'l10n_mx_edi', 'l10n_mx_edi_extended')
    util.move_field_to_module(cr, 'account.move.line', 'l10n_mx_edi_customs_number', 'l10n_mx_edi', 'l10n_mx_edi_extended')
    util.move_field_to_module(cr, 'account.move.line', 'l10n_mx_edi_umt_aduana_id', 'l10n_mx_edi', 'l10n_mx_edi_extended')
    util.move_field_to_module(cr, 'account.move.line', 'l10n_mx_edi_qty_umt', 'l10n_mx_edi', 'l10n_mx_edi_extended')
    util.move_field_to_module(cr, 'account.move.line', 'l10n_mx_edi_price_unit_umt', 'l10n_mx_edi', 'l10n_mx_edi_extended')

    util.create_column(cr, 'account_move', 'l10n_mx_edi_cfdi_request', 'varchar')

    cr.execute('''
        UPDATE account_move move
        SET l10n_mx_edi_cfdi_request = 'on_invoice'
        FROM res_company comp
        JOIN res_partner comp_partner ON comp_partner.id = comp.partner_id
        JOIN res_country country ON country.id = comp_partner.country_id
        WHERE comp.id = move.company_id
        AND move.move_type = 'out_invoice'
        AND UPPER(country.code) = 'MX'
    ''')

    cr.execute('''
        UPDATE account_move move
        SET l10n_mx_edi_cfdi_request = 'on_refund'
        FROM res_company comp
        JOIN res_partner comp_partner ON comp_partner.id = comp.partner_id
        JOIN res_country country ON country.id = comp_partner.country_id
        WHERE comp.id = move.company_id
        AND move.move_type = 'out_refund'
        AND UPPER(country.code) = 'MX'
    ''')

    cr.execute('''
        UPDATE account_move move
        SET l10n_mx_edi_cfdi_request = 'on_payment'
        FROM res_company comp
        JOIN res_partner comp_partner ON comp_partner.id = comp.partner_id
        JOIN res_country country ON country.id = comp_partner.country_id
        WHERE comp.id = move.company_id
        AND (move.payment_id IS NOT NULL OR move.statement_line_id IS NOT NULL) 
        AND UPPER(country.code) = 'MX'
    ''')

    cr.execute('''
        UPDATE account_move
        SET partner_bank_id = l10n_mx_edi_partner_bank_id
        WHERE l10n_mx_edi_cfdi_request IN ('on_invoice', 'on_refund')        
    ''')

    cr.execute('''
        UPDATE account_move
        SET
            l10n_mx_edi_payment_method_id = account_payment.l10n_mx_edi_payment_method_id,
            l10n_mx_edi_pac_status = account_payment.l10n_mx_edi_pac_status,
            l10n_mx_edi_sat_status = account_payment.l10n_mx_edi_sat_status,
            l10n_mx_edi_origin = account_payment.l10n_mx_edi_origin,
            partner_bank_id = account_payment.l10n_mx_edi_partner_bank_id,
            l10n_mx_edi_time_invoice = account_payment.l10n_mx_edi_time_payment
        FROM account_payment
        WHERE account_move.payment_id = account_payment.id
    ''')

    cr.execute('''
        UPDATE account_move
        SET l10n_mx_edi_payment_method_id = account_bank_statement_line.l10n_mx_edi_payment_method_id
        FROM account_bank_statement_line
        WHERE account_move.id = account_bank_statement_line.move_id
    ''')

    # product.template

    util.move_field_to_module(cr, 'product.template', 'l10n_mx_edi_tariff_fraction_id', 'l10n_mx_edi', 'l10n_mx_edi_extended')
    util.move_field_to_module(cr, 'product.template', 'l10n_mx_edi_umt_aduana_id', 'l10n_mx_edi', 'l10n_mx_edi_extended')

    # misc

    util.remove_model(cr, 'l10n_mx_edi.pac.sw.mixin')

    util.remove_field(cr, 'account.payment.register', 'l10n_mx_edi_partner_bank_id')

    util.move_model(cr, 'l10n_mx_edi.res.locality', 'l10n_mx_edi', 'l10n_mx_edi_extended', move_data=True)
    util.move_model(cr, 'l10n_mx_edi.tariff.fraction', 'l10n_mx_edi', 'l10n_mx_edi_extended', move_data=True)

    util.move_field_to_module(cr, 'res.company', 'l10n_mx_edi_locality', 'l10n_mx_edi', 'l10n_mx_edi_extended')
    util.move_field_to_module(cr, 'res.company', 'l10n_mx_edi_num_exporter', 'l10n_mx_edi', 'l10n_mx_edi_extended')
    util.move_field_to_module(cr, 'res.company', 'l10n_mx_edi_locality_id', 'l10n_mx_edi', 'l10n_mx_edi_extended')

    util.move_field_to_module(cr, 'res.config.settings', 'l10n_mx_edi_num_exporter', 'l10n_mx_edi', 'l10n_mx_edi_extended')

    util.move_field_to_module(cr, 'uom.uom', 'l10n_mx_edi_code_aduana', 'l10n_mx_edi', 'l10n_mx_edi_extended')

    util.move_field_to_module(cr, 'res.partner', 'l10n_mx_edi_locality', 'l10n_mx_edi', 'l10n_mx_edi_extended')
    util.move_field_to_module(cr, 'res.partner', 'l10n_mx_edi_locality_id', 'l10n_mx_edi', 'l10n_mx_edi_extended')
    util.move_field_to_module(cr, 'res.partner', 'l10n_mx_edi_curp', 'l10n_mx_edi', 'l10n_mx_edi_extended')
    util.move_field_to_module(cr, 'res.partner', 'l10n_mx_edi_external_trade', 'l10n_mx_edi', 'l10n_mx_edi_extended')

    # Migrate 'l10n_mx_edi_time_invoice' (char) to 'l10n_mx_edi_post_time' (datetime)

    cr.execute('''
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
        SET l10n_mx_edi_post_time = (LEFT(cfdi_per_move.date::varchar, 10) || ' ' || move.l10n_mx_edi_time_invoice || '.000000')::timestamp
        FROM cfdi_per_move
        WHERE cfdi_per_move.move_id = move.id
        AND cfdi_per_move.rank = 1
        AND LENGTH(move.l10n_mx_edi_time_invoice) = 8
    ''')

    # migrate to the new edi api.

    mx_edi_format_id = util.ref(cr, 'l10n_mx_edi.edi_cfdi_3_3')

    # Posted/signed invoices.
    cr.execute('''
        WITH cfdi_per_move AS (
            SELECT
                move.id AS move_id,
                attachment.id AS attachment_id,
                ROW_NUMBER() OVER(PARTITION BY move.id ORDER BY attachment.create_date DESC) AS rank
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
    ''', [mx_edi_format_id])

    # Posted/not signed invoices.
    cr.execute('''
        INSERT INTO account_edi_document (edi_format_id, move_id, state)
        SELECT
            %s,
            account_move.id,
            'to_send'
        FROM account_move
        WHERE account_move.l10n_mx_edi_pac_status IN ('retry', 'to_sign')
        AND account_move.state = 'posted'
    ''', [mx_edi_format_id])

    # Cleanup account.bank.statement.line

    util.remove_field(cr, 'account.bank.statement.line', 'l10n_mx_edi_payment_method_id')

    # Cleanup account.payment

    util.remove_field(cr, 'account.payment', 'l10n_mx_edi_pac_status')
    util.remove_field(cr, 'account.payment', 'l10n_mx_edi_sat_status')
    util.remove_field(cr, 'account.payment', 'l10n_mx_edi_payment_method_id')
    util.remove_field(cr, 'account.payment', 'l10n_mx_edi_origin')
    util.remove_field(cr, 'account.payment', 'l10n_mx_edi_cfdi')
    util.remove_field(cr, 'account.payment', 'l10n_mx_edi_expedition_date')
    util.remove_field(cr, 'account.payment', 'l10n_mx_edi_time_payment')
    util.remove_field(cr, 'account.payment', 'l10n_mx_edi_partner_bank_id')
    util.remove_field(cr, 'account.payment', 'l10n_mx_edi_cfdi_name')

    # Cleanup account.move

    util.remove_field(cr, 'account.move', 'l10n_mx_edi_cfdi_name')
    util.remove_field(cr, 'account.move', 'l10n_mx_edi_partner_bank_id')
    util.remove_field(cr, 'account.move', 'l10n_mx_edi_cfdi')
    util.remove_field(cr, 'account.move', 'l10n_mx_edi_time_invoice')
    util.remove_field(cr, 'account.move', 'l10n_mx_edi_pac_status')
    util.remove_field(cr, 'account.move.line', 'l10n_mx_edi_tariff_fraction_id')
