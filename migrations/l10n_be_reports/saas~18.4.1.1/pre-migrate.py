from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "l10n_be_reports_isoc_prepayment_pay_wizard", "corporate_tax_rate")
