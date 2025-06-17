from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "l10n_be_reports.vat.return.submission.wizard", "need_ec_sales_list")
