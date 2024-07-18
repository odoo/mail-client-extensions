from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE hr_expense
           SET payment_mode = 'own_account'
         WHERE payment_mode IS NULL
        """,
        table="hr_expense",
    )
