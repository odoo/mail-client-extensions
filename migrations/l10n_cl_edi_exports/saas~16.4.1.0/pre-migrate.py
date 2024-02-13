from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_cl_edi_exports.report_invoice_document")
