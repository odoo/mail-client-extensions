from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_payment", "bacs_ddi_id", "int4")
    util.explode_execute(
        cr,
        query="""
            UPDATE account_payment
               SET bacs_ddi_id = account_move.bacs_ddi_id
              FROM account_move
             WHERE account_move.id = account_payment.move_id
               AND account_move.bacs_ddi_id IS NOT NULL
        """,
        table="account_payment",
    )
    util.remove_column(cr, "account_move", "bacs_ddi_id")  # the field is now computed
