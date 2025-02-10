from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "is_closing", "boolean", default=False)

    query = """
        UPDATE sale_order so
           SET is_closing = TRUE
          FROM sale_subscription_plan sp
         WHERE so.plan_id = sp.id
           AND so.subscription_state IN ('3_progress', '4_paused')
           AND sp.user_closable = TRUE
           AND so.end_date IS NOT NULL
           AND so.next_invoice_date IS NOT NULL
           AND so.end_date <= so.next_invoice_date
    """
    util.explode_execute(cr, query, table="sale_order", alias="so")
