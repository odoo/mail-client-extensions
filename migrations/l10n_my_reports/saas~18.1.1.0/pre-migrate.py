from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.partner", "active_company_country_code")
