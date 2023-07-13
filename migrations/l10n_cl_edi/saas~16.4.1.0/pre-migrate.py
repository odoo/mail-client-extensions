from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_cl_edi.envio_receipt_dte")
    util.remove_view(cr, "l10n_cl_edi.receipt_dte")
