from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_mx_edi_external_trade", "boolean")
