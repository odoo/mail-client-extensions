import logging

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # ORM Way
    _table_name = "account_move_line" if util.version_gte("saas~12.4") else "account_invoice_line"
    query = util.format_query(
        cr,
        """
        SELECT id
          FROM {}
         WHERE subscription_end_date IS NOT NULL
           AND subscription_start_date IS NOT NULL
        """,
        _table_name,
    )
    util.recompute_fields(cr, util.model_of_table(cr, _table_name), ["subscription_mrr"], query=query)

    # #SQL Way
    # Tried to use the PostgreSQL "age" function
    # https://www.postgresql.org/docs/11/functions-datetime.html
    #
    # With inputs like :
    # subscription_start_date | subscription_end_date
    # ------------------------+-----------------------
    # 2017-01-30              | 2017-02-27
    #
    # Leads to 29 days in SQL, while 1 month in Python.
    # The python result seems correct while the PostgreSQL one not
    # Kept the ORM way until founding an SQL accuyrate solution
    # cr.execute("""
    #     UPDATE account_invoice_line
    #        SET subscription_mrr2=price_subtotal_signed/(EXTRACT(YEAR FROM s.delta) * 12 + EXTRACT(MONTH FROM s.delta) + EXTRACT(DAY FROM s.delta) / 30)
    #       FROM (SELECT id, age(subscription_end_date + integer '1', subscription_start_date) as delta
    #              FROM account_invoice_line
    #             WHERE subscription_end_date IS NOT NULL
    #               AND subscription_start_date IS NOT NULL) as s
    #      WHERE account_invoice_line.id=s.id
    #        AND (EXTRACT(YEAR FROM s.delta) * 12 + EXTRACT(MONTH FROM s.delta) + EXTRACT(DAY FROM s.delta) / 30) != 0
    # """)
