from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "res_partner", "l10n_de_datev_identifier")
    util.remove_column(cr, "res_partner", "l10n_de_datev_identifier_customer")
