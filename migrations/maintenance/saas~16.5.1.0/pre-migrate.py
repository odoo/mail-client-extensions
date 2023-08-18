# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "maintenance_request", "recurring_maintenance", "boolean")
    util.create_column(cr, "maintenance_request", "repeat_interval", "int4")
    util.create_column(cr, "maintenance_request", "repeat_unit", "varchar")
    util.create_column(cr, "maintenance_request", "repeat_type", "varchar")
    util.create_column(cr, "maintenance_request", "repeat_until", "date")

    query = """
        UPDATE maintenance_request r
           SET repeat_interval = e.period,
               repeat_unit = 'day',
               repeat_type = 'forever',
               recurring_maintenance = true
          FROM maintenance_equipment e
         WHERE r.equipment_id = e.id
           AND e.period > 0
           AND r.stage_id NOT IN (select id from maintenance_stage where done=true)
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="maintenance_request", alias="r"))

    util.remove_field(cr, "maintenance.equipment", "period")
    util.remove_field(cr, "maintenance.equipment", "next_action_date")
    util.remove_field(cr, "maintenance.equipment", "maintenance_duration")

    util.remove_record(cr, "maintenance.maintenance_requests_cron")
