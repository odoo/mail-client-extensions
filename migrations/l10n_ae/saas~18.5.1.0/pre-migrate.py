from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_ae.document_tax_totals_company_currency_template")
    util.remove_view(cr, "l10n_ae.report_invoice_document")
    util.remove_field(cr, "account.move.line", "l10n_ae_vat_amount")
