from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_commission_plan_target", "payment_date", "date")
    util.create_column(cr, "sale_commission_plan_target", "payment_amount", "numeric")
    cr.execute(
        """
        WITH _targets AS (
            SELECT UNNEST(ARRAY_AGG(id)) as id,
                   date_to,
                   SUM(amount) as amount
              FROM sale_commission_plan_target
          GROUP BY plan_id, date_to
        )
        UPDATE sale_commission_plan_target t
           SET payment_date = o.date_to,
               payment_amount = o.amount
          FROM _targets o
         WHERE o.id = t.id
        """
    )
