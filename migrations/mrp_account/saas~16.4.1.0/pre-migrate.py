# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Convert the old analytic_account_id field to a 100% distribution on this specific account for MO
    util.create_column(cr, "mrp_production", "analytic_distribution", "jsonb")
    query = """
            UPDATE mrp_production p
            SET analytic_distribution = jsonb_build_object(analytic_account_id, 100.0)
            WHERE analytic_account_id IS NOT NULL
    """
    util.explode_execute(cr, query, table="mrp_production", alias="p")
    util.create_m2m(cr, "account_analytic_account_mrp_production_rel", "mrp_production", "account_analytic_account")
    query = """
            INSERT INTO account_analytic_account_mrp_production_rel (mrp_production_id, account_analytic_account_id)
            SELECT id, analytic_account_id FROM mrp_production WHERE analytic_account_id IS NOT NULL
        """
    cr.execute(query)
    util.remove_field(cr, "mrp.production", "analytic_account_id")

    # Convert the old costs_hour_account_id field to a 100% distribution on this specific account for WC
    util.create_column(cr, "mrp_workcenter", "analytic_distribution", "jsonb")
    query = """
        UPDATE mrp_workcenter w
        SET analytic_distribution = jsonb_build_object(costs_hour_account_id, 100.0)
        WHERE costs_hour_account_id IS NOT NULL
    """
    util.explode_execute(cr, query, table="mrp_workcenter", alias="w")
    util.create_m2m(cr, "account_analytic_account_mrp_workcenter_rel", "mrp_workcenter", "account_analytic_account")
    query = """
        INSERT INTO account_analytic_account_mrp_workcenter_rel (mrp_workcenter_id, account_analytic_account_id)
        SELECT id, costs_hour_account_id FROM mrp_workcenter WHERE costs_hour_account_id IS NOT NULL
    """
    cr.execute(query)
    util.remove_field(cr, "mrp.workcenter", "costs_hour_account_id")

    # Convert the old Many2one analytic_account_line_id fields to Many2many fields for the workorder
    util.create_m2m(cr, "mrp_workorder_mo_analytic_rel", "mrp_workorder", "account_analytic_line")
    query = """
        INSERT INTO mrp_workorder_mo_analytic_rel (mrp_workorder_id, account_analytic_line_id)
        SELECT id, mo_analytic_account_line_id FROM mrp_workorder WHERE mo_analytic_account_line_id IS NOT NULL
    """
    cr.execute(query)
    util.remove_field(cr, "mrp.workorder", "mo_analytic_account_line_id")

    util.create_m2m(cr, "mrp_workorder_wc_analytic_rel", "mrp_workorder", "account_analytic_line")
    query = """
        INSERT INTO mrp_workorder_wc_analytic_rel (mrp_workorder_id, account_analytic_line_id)
        SELECT id, wc_analytic_account_line_id FROM mrp_workorder WHERE wc_analytic_account_line_id IS NOT NULL
    """
    cr.execute(query)
    util.remove_field(cr, "mrp.workorder", "wc_analytic_account_line_id")
