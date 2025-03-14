from odoo.upgrade import util


def migrate(cr, version):
    # The default for allow_out_payment is False except for pre-existing bank accounts
    util.create_column(cr, "res_partner_bank", "allow_out_payment", "bool")
    cr.execute("UPDATE res_partner_bank SET allow_out_payment = true")
