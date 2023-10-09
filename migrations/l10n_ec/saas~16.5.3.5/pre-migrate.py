from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.journal", "l10n_ec_emission_type")
