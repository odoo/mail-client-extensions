# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "crm.lead", "expected_revenue", "prorated_revenue")
    util.rename_field(cr, "crm.lead", "planned_revenue", "expected_revenue")

    util.create_column(cr, "crm_lead", "recurring_plan", "int4")

    # For PG >= 11, default values are quick
    # for older version, it's as slow as an `UPDATE`, so better doing it only once
    # See 5c9ac195484916b2e0d3308e270a5075a7bd5057
    kw = {"default": 0} if cr._cnx.server_version >= 110000 else {}
    util.create_column(cr, "crm_lead", "recurring_revenue", "numeric", **kw)
    util.create_column(cr, "crm_lead", "recurring_revenue_monthly", "numeric", **kw)
    util.create_column(cr, "crm_lead", "recurring_revenue_monthly_prorated", "numeric", **kw)

    if not kw:
        query = """
            UPDATE crm_lead
               SET recurring_revenue = COALESCE(recurring_revenue, 0),
                   recurring_revenue_monthly = COALESCE(recurring_revenue_monthly, 0),
                   recurring_revenue_monthly_prorated = COALESCE(recurring_revenue_monthly_prorated, 0)
             WHERE (recurring_revenue IS NULL
                OR recurring_revenue_monthly IS NULL
                OR recurring_revenue_monthly_prorated IS NULL)
        """
        util.parallel_execute(cr, util.explode_query_range(cr, query, table="crm_lead"))
