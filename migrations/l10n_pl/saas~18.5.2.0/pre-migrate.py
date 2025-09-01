from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_pl.report_invoice_document")
