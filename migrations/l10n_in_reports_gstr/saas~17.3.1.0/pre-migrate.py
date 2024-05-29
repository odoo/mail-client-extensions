from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "l10n_in_gstr_gst_otp")
    util.remove_field(cr, "res.config.settings", "l10n_in_gstr_gst_token")

    util.remove_view(cr, "l10n_in_reports_gstr.view_get_otp_validate_wizard")
