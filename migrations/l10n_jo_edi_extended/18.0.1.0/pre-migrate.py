from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "l10n_jo_edi_payment_method")
