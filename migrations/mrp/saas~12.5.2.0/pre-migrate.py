# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "mrp.sequence_mrp_unbuild", True)

    util.create_column(cr, "mrp_bom_line", "company_id", "int4")
    util.explode_execute(
        cr,
        """
        UPDATE mrp_bom_line l
           SET company_id = b.company_id
          FROM mrp_bom b
         WHERE b.id = l.bom_id
        """,
        table="mrp_bom_line",
        alias="l",
    )

    util.rename_field(cr, "mrp.bom.line", "attribute_value_ids", "bom_product_template_attribute_value_ids")
    util.create_m2m(
        cr, "mrp_bom_line_product_template_attribute_value_rel", "mrp_bom_line", "product_template_attribute_value"
    )
    cr.execute(
        """
        INSERT INTO mrp_bom_line_product_template_attribute_value_rel(mrp_bom_line_id, product_template_attribute_value_id)
             SELECT r.mrp_bom_line_id, ptav.id
               FROM mrp_bom_line_product_attribute_value_rel r
               JOIN product_template_attribute_value ptav ON ptav.product_attribute_value_id = r.product_attribute_value_id
               JOIN mrp_bom_line bline ON bline.id = r.mrp_bom_line_id
               JOIN mrp_bom b ON b.id = bline.bom_id
              WHERE ptav.product_tmpl_id = b.product_tmpl_id
    """
    )
    cr.execute("DROP TABLE mrp_bom_line_product_attribute_value_rel CASCADE")
    util.remove_field(cr, "mrp.bom.line", "valid_product_attribute_value_ids")

    if util.table_exists(cr, "mrp_bom_byproduct"):
        util.create_column(cr, "mrp_bom_byproduct", "company_id", "int4")
        util.create_column(cr, "mrp_bom_byproduct", "routing_id", "int4")
        cr.execute(
            """
            UPDATE mrp_bom_byproduct y
               SET company_id = b.company_id,
                   routing_id = b.routing_id
              FROM mrp_bom b
             WHERE b.id = y.bom_id
        """
        )

    util.remove_field(cr, "mrp.production", "date_planned_start_wo")
    util.remove_field(cr, "mrp.production", "date_planned_finished_wo")
    util.create_column(cr, "mrp_production", "date_deadline", "timestamp without time zone")  # rename?

    util.create_column(cr, "mrp_routing_workcenter", "worksheet_type", "varchar")
    util.create_column(cr, "mrp_routing_workcenter", "worksheet_google_slide", "varchar")
    cr.execute(
        """
        UPDATE mrp_routing_workcenter mrw
        SET worksheet_type='pdf'
        WHERE EXISTS (
            SELECT 1
            FROM ir_attachment
            WHERE res_model='mrp.routing.workcenter'
              AND res_field='worksheet'
              AND res_id=mrw.id
        )
    """
    )

    util.create_column(cr, "mrp_unbuild", "company_id", "int4")
    cr.execute(
        """
        UPDATE mrp_unbuild u
           SET company_id = b.company_id
          FROM mrp_bom b
         WHERE b.id = u.bom_id
    """
    )

    util.create_column(cr, "mrp_workcenter_productivity", "company_id", "int4")
    cr.execute(
        """
        UPDATE mrp_workcenter_productivity p
           SET company_id = w.company_id
          FROM mrp_workcenter w
         WHERE w.id = p.workcenter_id
    """
    )

    util.create_column(cr, "mrp_workorder", "company_id", "int4")
    util.create_column(cr, "mrp_workorder", "date_planned_start", "timestamp without time zone")  # rename?
    util.create_column(cr, "mrp_workorder", "date_planned_finished", "timestamp without time zone")  # rename?
    cr.execute(
        """
        UPDATE mrp_workorder o
           SET company_id = c.company_id
          FROM mrp_workcenter c
         WHERE c.id = o.workcenter_id
    """
    )
    cr.execute(
        """
        UPDATE mrp_workorder o
           SET date_planned_start = l.date_from,
               date_planned_finished = l.date_to
          FROM resource_calendar_leaves l
         WHERE l.id = o.leave_id
    """
    )

    util.create_column(cr, "stock_warehouse", "manufacture_mto_pull_id", "int4")
    util.remove_field(cr, "report.stock.forecast", "production_id")

    cr.execute("TRUNCATE mrp_product_produce CASCADE")  # transient model
    util.create_column(cr, "mrp_product_produce", "production_id", "int4")

    util.remove_record(cr, "mrp.menu_view_resource_calendar_search_mrp")
    util.remove_record(cr, "mrp.menu_mrp_workcenter_productivity_loss")
