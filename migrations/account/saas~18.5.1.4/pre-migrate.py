from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, model="res.partner", fieldname="duplicated_bank_account_partners_count")
    util.remove_field(cr, model="res.company", fieldname="account_sale_receipt_tax_id")
    util.remove_field(cr, model="res.company", fieldname="account_purchase_receipt_tax_id")

    util.create_column(cr, "account_move_line", "no_followup", "bool")
    util.explode_execute(
        cr,
        """
        UPDATE account_move_line l
           SET no_followup = True
          FROM account_move m
         WHERE l.move_id = m.id
           AND m.move_type = 'entry'
           AND m.origin_payment_id IS NULL
        """,
        table="account_move_line",
        alias="l",
    )
