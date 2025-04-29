from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "pos_amount_unsettled", "numeric")
    util.explode_execute(cr, "UPDATE account_move SET pos_amount_unsettled = amount_residual", table="account_move")

    util.create_column(cr, "pos_order", "commercial_partner_id", "int4")
    util.explode_execute(
        cr,
        """
        UPDATE pos_order AS o
           SET commercial_partner_id = p.commercial_partner_id
          FROM res_partner AS p
         WHERE o.partner_id = p.id
        """,
        table="pos_order",
        alias="o",
    )
