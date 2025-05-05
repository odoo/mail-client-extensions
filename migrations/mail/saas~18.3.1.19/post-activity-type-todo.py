from odoo.upgrade import util


def migrate(cr, version):
    todo = util.ref(cr, "mail.mail_activity_data_todo")
    updoc = util.ref(cr, "mail.mail_activity_data_upload_document")
    xmlids = [
        "sale.mail_act_sale_upsell",
        "product_expiry.mail_activity_type_alert_date_reached",
        "mrp_plm.mail_activity_eco_approval",
        "website_slides.mail_activity_data_access_request",
        "documents.mail_documents_activity_data_tv",
        "documents_account.mail_documents_activity_data_vat",
        "documents_account.mail_documents_activity_data_fs",
        "account_online_synchronization.bank_sync_activity_update_consent",
        "l10n_be_reports.ec_sales_list_activity",
        "l10n_be_reports.partner_vat_listing_report_activity",
    ]

    mapping = {act: todo for xmlid in xmlids if (act := util.ref(cr, xmlid)) is not None}

    xmlid = "documents.mail_documents_activity_data_md"
    if act := util.ref(cr, xmlid):
        mapping[act] = updoc
        xmlids.append(xmlid)

    if mapping:
        util.replace_record_references_batch(cr, mapping, "mail.activity.type", replace_xmlid=False)
    util.delete_unused(cr, *xmlids)
