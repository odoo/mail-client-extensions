from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_uk_reports_cis.hmrc_cis_monthly_return_body")
