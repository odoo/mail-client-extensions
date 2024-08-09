from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "l10n_in.gst.return.period", "invoice_amount")
    util.remove_field(cr, "l10n_in.gst.return.period", "bill_amount")
    util.remove_field(cr, "l10n_in.gst.return.period", "expected_amount")
