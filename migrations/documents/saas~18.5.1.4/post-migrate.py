from odoo.upgrade import util


def migrate(cr, version):
    # Create new forcecreate=0 folders
    for folder_xmlid in (
        "documents.document_finance_social_folder",
        "documents.document_finance_taxes_folder",
        "documents.document_finance_taxes_folder",
        "documents.document_finance_annual_closing_folder",
        "documents.document_finance_annual_closing_year_current_folder",
        "documents.document_legal_folder",
        "documents.document_insurances_folder",
        "documents.document_loans_folder",
        "documents.document_registrations_folder",
        "documents.document_contracts_folder",
    ):
        util.update_record_from_xml(cr, folder_xmlid)
        util.force_noupdate(cr, folder_xmlid, noupdate=True)

    util.delete_unused(cr, "documents.ir_actions_server_tag_add_validated")

    # Remove deprecated tags
    util.delete_unused(
        cr,
        "documents.documents_tag_draft",
        "documents.documents_tag_inbox",
        "documents.documents_tag_to_validate",
        "documents.documents_tag_validated",
        "documents.documents_tag_deprecated",
        "documents.documents_tag_sales",
        "documents.documents_tag_other",
        "documents.documents_tag_presentations",
        "documents.documents_tag_project",
        "documents.documents_tag_text",
        "documents.documents_tag_bill",
        "documents.documents_tag_expense",
        "documents.documents_tag_vat",
        "documents.documents_tag_fiscal",
        "documents.documents_tag_financial",
        "documents.documents_tag_ads",
        "documents.documents_tag_brochures",
        "documents.documents_tag_images",
        "documents.documents_tag_videos",
    )

    util.update_record_from_xml(cr, "documents.mail_template_document_share")
