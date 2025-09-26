from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move_send", "l10n_it_edi_checkbox_send", "boolean")
    util.create_column(cr, "account_move", "l10n_it_edi_state", "varchar")
    util.create_column(cr, "account_move", "l10n_it_edi_header", "text")

    util.rename_field(cr, "res.config.settings", "l10n_it_edi_sdicoop_register", "l10n_it_edi_register")
    util.rename_field(cr, "res.config.settings", "l10n_it_edi_sdicoop_demo_mode", "l10n_it_edi_demo_mode")

    util.remove_view(cr, "l10n_it_edi.view_out_invoice_tree_inherit")
    util.remove_view(cr, "l10n_it_edi.view_in_bill_tree_inherit")
    util.remove_view(cr, "l10n_it_edi.account_invoice_form_l10n_it_pa")

    query = """
         UPDATE account_move am
            SET l10n_it_edi_state = CASE
                    WHEN aed.state = 'to_send' AND am.l10n_it_edi_transaction IS NULL AND aed.blocking_level = 'error' THEN 'rejected'
                    WHEN aed.state = 'to_send' AND am.l10n_it_edi_transaction IS NULL THEN NULL
                    WHEN aed.state = 'to_send' AND am.l10n_it_edi_transaction IS NOT NULL THEN 'processing'
                    WHEN aed.state = 'sent' THEN 'forwarded'
                END,
                l10n_it_edi_header = REPLACE(aed.error, '<ul>', '<ul class="mb-0">')
           FROM account_edi_document aed
           JOIN account_edi_format aef
             ON aef.id = aed.edi_format_id
            AND aef.code = 'fattura_pa'
          WHERE am.state = 'posted'
            AND aed.move_id = am.id
    """
    util.explode_execute(cr, query, table="account_move", alias="am")

    query = """
        UPDATE ir_attachment ia
           SET res_field = 'l10n_it_edi_attachment_file',
               mimetype = 'application/xml'
          FROM account_move am
         WHERE ia.id = am.l10n_it_edi_attachment_id
    """
    util.explode_execute(cr, query, table="ir_attachment", alias="ia")

    util.remove_field(cr, "account.move", "l10n_it_einvoice_id")
    util.remove_field(cr, "account.move", "l10n_it_einvoice_name")
    util.remove_field(cr, "account.move", "l10n_it_edi_attachment_id")
