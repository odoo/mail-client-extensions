# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "crm.lead", "expected_revenue", "prorated_revenue")
    util.rename_field(cr, "crm.lead", "planned_revenue", "expected_revenue")
    util.create_column(cr, "crm_lead", "recurring_revenue_monthly", "numeric", default=0.0)
    util.create_column(cr, "crm_lead", "recurring_revenue_monthly_prorated", "numeric", default=0.0)
    util.create_column(cr, "crm_lead", "recurring_revenue", "numeric")
    util.create_column(cr, "crm_lead", "recurring_plan", "int4")
