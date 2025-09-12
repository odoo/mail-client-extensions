from odoo.upgrade import util


def migrate(cr, version):
    query = """
        SELECT id
          FROM hr_expense
         WHERE total_amount_company is NULL
           AND unit_amount = 0.00
        """
    util.recompute_fields(cr, "hr.expense", ["total_amount_company"], query=query)

    query = """
        UPDATE hr_expense he
           SET unit_amount = ROUND(he.total_amount_company / CASE WHEN he.quantity = 0 THEN 1 ELSE he.quantity END, rc.decimal_places)
          FROM res_currency rc
         WHERE he.currency_id = rc.id
           AND he.unit_amount = 0.00
    """
    util.explode_execute(cr, query, table="hr_expense", alias="he")

    query = """
        UPDATE account_move_line line
           SET price_unit = he.unit_amount
          FROM hr_expense he
         WHERE line.expense_id = he.id
           AND line.debit != 0
           AND line.payment_id IS NULL
    """
    util.explode_execute(cr, query, table="account_move_line", alias="line")
    # get the id of above updated records
    cr.execute(
        """
        SELECT line.id, line.move_id
          FROM account_move_line line
          JOIN hr_expense he
            ON line.expense_id = he.id
         WHERE line.debit != 0
           AND line.payment_id IS NULL
        """
    )
    data = cr.fetchall()
    move_line_ids = [id[0] for id in data]
    util.recompute_fields(cr, "account.move.line", ["price_subtotal"], ids=move_line_ids)
    move_ids = list({id[1] for id in data})
    util.recompute_fields(cr, "account.move", ["amount_residual"], ids=move_ids)
