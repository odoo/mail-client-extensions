from odoo.upgrade import util


def migrate(cr, version):
    module = "l10n_in_reports" if util.version_gte("saas~18.2") else "l10n_in_reports_gstr"
    util.remove_view(cr, f"{module}.l10n_in_gst_return_period_view_inherit_spreadsheet")
    util.rename_field(cr, "l10n_in.gst.return.period", "gstr1_spreadsheet", "gstr1_spreadsheet_id")
    util.change_field_selection_values(
        cr, "l10n_in.gst.return.period", "gstr2b_status", {"not_recived": "not_received"}
    )
