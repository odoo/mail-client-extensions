from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_in_reports_gstr.l10n_in_gst_return_period_view_inherit_spreadsheet")
    util.rename_field(cr, "l10n_in.gst.return.period", "gstr1_spreadsheet", "gstr1_spreadsheet_id")
