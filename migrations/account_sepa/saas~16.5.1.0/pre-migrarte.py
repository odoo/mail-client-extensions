from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_payment", "sepa_uetr", "varchar")
