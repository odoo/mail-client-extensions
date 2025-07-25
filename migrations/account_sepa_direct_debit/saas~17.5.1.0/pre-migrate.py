from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, model="sdd.mandate", fieldname="payment_journal_id")
    util.remove_field(cr, model="sdd.mandate", fieldname="suitable_journal_ids")
    util.create_column(cr, table="sdd_mandate", column="is_sent", definition="boolean")
    util.create_column(cr, table="account_payment", column="sdd_mandate_id", definition="int4")
    util.create_column(cr, "sdd_mandate", "expiration_warning_already_sent", "boolean")

    util.explode_execute(
        cr,
        query="UPDATE sdd_mandate SET is_sent = true WHERE state = 'active'",
        table="sdd_mandate",
    )
    util.explode_execute(
        cr,
        query="""
            UPDATE account_payment
               SET sdd_mandate_id = account_move.sdd_mandate_id
              FROM account_move
             WHERE account_move.id = account_payment.move_id
               AND account_move.sdd_mandate_id IS NOT NULL
        """,
        table="account_payment",
    )
    util.remove_column(cr, "account_move", "sdd_mandate_id")  # the field is now related from payment to move
    util.remove_field(cr, "account.move", "sdd_mandate_scheme")
