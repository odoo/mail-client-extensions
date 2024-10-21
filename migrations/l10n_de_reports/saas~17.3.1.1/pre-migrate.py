from odoo.upgrade import util


def migrate(cr, version):
    util.make_field_company_dependent(cr, "res.partner", "l10n_de_datev_identifier", "integer")
    util.make_field_company_dependent(cr, "res.partner", "l10n_de_datev_identifier_customer", "integer")
