from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_my_edi_pos.view_tax_form_inherit_l10n_my_edi_pos")
    # These views are replaced by the new ones in the base module.
    util.remove_view(cr, "l10n_my_edi_pos.myinvois_consolidate_invoice_wizard_form")
    util.remove_view(cr, "l10n_my_edi_pos.myinvois_document_status_update_form")
    util.remove_view(cr, "l10n_my_edi_pos.myinvois_document_form_view")
    util.remove_view(cr, "l10n_my_edi_pos.myinvois_document_list_view")

    util.move_field_to_module(cr, "account.tax", "l10n_my_tax_exemption_reason", "l10n_my_edi_pos", "l10n_my_edi")

    util.move_model(cr, "myinvois.consolidate.invoice.wizard", "l10n_my_edi_pos", "l10n_my_edi")
    util.move_model(cr, "myinvois.document.status.update.wizard", "l10n_my_edi_pos", "l10n_my_edi")
    util.move_model(
        cr,
        "myinvois.document",
        "l10n_my_edi_pos",
        "l10n_my_edi",
        move_data=True,
        keep=(
            "action_consolidated_invoices",
            "myinvois_document_pos_list_view",
            "myinvois_document_pos_form_view",
        ),
    )
