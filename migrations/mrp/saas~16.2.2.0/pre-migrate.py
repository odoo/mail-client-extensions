# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mrp_bom", "produce_delay", "double precision")
    util.create_column(cr, "mrp_bom", "days_to_prepare_mo", "double precision")
    query = """
        UPDATE mrp_bom b
           SET produce_delay = pt.produce_delay,
               days_to_prepare_mo = pt.days_to_prepare_mo
          FROM product_template pt
         WHERE b.product_tmpl_id = pt.id
           AND (pt.produce_delay <> 0 OR pt.days_to_prepare_mo <> 0)
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="mrp_bom", alias="b"))
    util.remove_field(cr, "product.template", "produce_delay")
    util.remove_field(cr, "product.template", "days_to_prepare_mo")

    util.explode_execute(
        cr,
        "UPDATE mrp_production SET date_start=date_planned_start WHERE date_start IS NULL",
        table="mrp_production",
    )
    util.explode_execute(
        cr,
        "UPDATE mrp_production SET date_finished=date_planned_finished WHERE date_finished IS NULL",
        table="mrp_production",
    )

    util.adapt_domains(cr, "mrp.production", "date_planned_start", "date_start")
    util.adapt_domains(cr, "mrp.production", "date_planned_finished", "date_finished")

    util.remove_field(cr, "mrp.production", "date_planned_start")
    util.remove_field(cr, "mrp.production", "date_planned_finished")

    util.rename_field(cr, "mrp.production", "production_duration_expected", "duration_expected")
    util.rename_field(cr, "mrp.production", "production_real_duration", "duration")

    util.explode_execute(
        cr,
        "UPDATE mrp_workorder SET date_start=date_planned_start WHERE date_start IS NULL",
        table="mrp_workorder",
    )
    util.explode_execute(
        cr,
        "UPDATE mrp_workorder SET date_finished=date_planned_finished WHERE date_finished IS NULL",
        table="mrp_workorder",
    )

    util.adapt_domains(cr, "mrp.workorder", "date_planned_start", "date_start")
    util.adapt_domains(cr, "mrp.workorder", "date_planned_finished", "date_finished")

    util.remove_field(cr, "mrp.workorder", "date_planned_start")
    util.remove_field(cr, "mrp.workorder", "date_planned_finished")
