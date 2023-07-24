from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "account.move", "l10n_mx_edi_origin", "l10n_mx_edi_cfdi_origin")
    util.rename_field(cr, "account.move", "l10n_mx_edi_cancel_move_id", "l10n_mx_edi_cfdi_cancel_id")
    util.rename_field(cr, "account.move", "l10n_mx_edi_sat_status", "l10n_mx_edi_cfdi_sat_state")
    util.change_field_selection_values(
        cr,
        "account.move",
        "l10n_mx_edi_cfdi_sat_state",
        {
            "undefined": None,
            "none": None,
        },
    )

    util.create_column(cr, "account_move", "l10n_mx_edi_is_cfdi_needed", "bool")
    util.create_column(cr, "account_move", "l10n_mx_edi_cfdi_attachment_id", "int4")
    util.create_column(cr, "account_move", "l10n_mx_edi_cfdi_state", "varchar")

    query = """
        UPDATE account_move
        SET l10n_mx_edi_is_cfdi_needed = True
        WHERE l10n_mx_edi_cfdi_request IS NOT NULL
    """
    util.explode_execute(cr, query, table="account_move")

    util.remove_field(cr, "account.move", "l10n_mx_edi_cfdi_request")
    util.remove_field(cr, "account.bank.statement.line", "l10n_mx_edi_force_generate_cfdi")
    util.remove_field(cr, "account.payment", "l10n_mx_edi_force_generate_cfdi")

    util.remove_record(cr, "l10n_mx_edi.action_report_payment_receipt")
    util.rename_xmlid(
        cr, "l10n_mx_edi.view_account_journal_form_inh_l10n_mx", "l10n_mx_edi.account_journal_form_inherit_l10n_mx_edi"
    )
    util.rename_xmlid(
        cr, "l10n_mx_edi.view_l10n_mx_edi_invoice_form_inherit", "l10n_mx_edi.account_move_form_inherit_l10n_mx_edi"
    )

    util.remove_view(cr, "l10n_mx_edi.report_invoice_document_mx")
    util.remove_view(cr, "l10n_mx_edi.report_payment_document_mx")
    util.remove_view(cr, "l10n_mx_edi.report_payment_receipt")
    util.remove_view(cr, "l10n_mx_edi.report_payment_receipt_document")
    util.remove_view(cr, "l10n_mx_edi.view_bank_statement_line_tree_bank_rec_widget_inh_l10n_mx")
    util.remove_view(cr, "l10n_mx_edi.view_account_payment_form_inh_l10n_mx")
