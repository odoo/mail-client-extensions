from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "l10n_in_gst_treatment")
    util.remove_view(cr, "l10n_in_sale.gst_report_saleorder_document_inherit")
