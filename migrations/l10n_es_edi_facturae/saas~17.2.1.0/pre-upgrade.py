from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_es_payment_means", "varchar", default="04")
