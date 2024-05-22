from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.contract", "l10n_sa_company_country_code")
