from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account_reports.export.wizard", "l10n_be_reports_periodic_vat_wizard_id")
    util.remove_model(cr, "l10n_be_reports.periodic.vat.xml.export")

    todo = util.ref(cr, "mail.mail_activity_data_todo")
    mapping = {
        act: todo
        for xmlid in ["ec_sales_list_activity", "partner_vat_listing_report_activity"]
        if (act := util.ref(cr, f"l10n_be_reports.{xmlid}")) is not None
    }
    if mapping:
        util.replace_record_references_batch(cr, mapping, "mail.activity.type", replace_xmlid=False)
    util.delete_unused(
        cr, "l10n_be_reports.ec_sales_list_activity", "l10n_be_reports.partner_vat_listing_report_activity"
    )
