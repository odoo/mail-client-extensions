from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_cz_scheme_code", "varchar", default="0")
