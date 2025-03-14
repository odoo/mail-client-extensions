from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "crm_lead", "recurring_revenue_prorated", "numeric")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
        UPDATE crm_lead
           SET recurring_revenue_prorated = COALESCE(recurring_revenue, 0.0) * COALESCE(probability, 0.0) / 100.0
            """,
            table="crm_lead",
        ),
    )
