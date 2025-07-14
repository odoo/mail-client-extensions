from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.journal", "l10n_sa_serial_number")
