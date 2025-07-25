from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "account_return", "v19_l10n_in_return_period_id")
    util.remove_model(cr, "l10n_in.gst.return.period")
    cr.execute("DROP TABLE ir_attachment_l10n_in_gst_return_period_rel")
    cr.execute("DROP TABLE irn_attachment_portal_json")
