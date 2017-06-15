# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'project_forecast', 'employee_id', 'int4')
    util.remove_field(cr, 'project.forecast.assignment', 'user_id')     # transient model

    cr.execute("""
        WITH user_resources AS (
            SELECT (array_agg(id ORDER BY name))[1] as id, user_id
              FROM resource_resource
             WHERE resource_type = 'user'
               AND user_id IS NOT NULL
          GROUP BY user_id
        )
        UPDATE project_forecast f
           SET employee_id = e.id
          FROM user_resources r JOIN hr_employee e ON (r.id = e.resource_id)
         WHERE r.user_id = f.user_id
    """)

    fields = ['effective_hours', 'percentage_hours']
    if util.module_installed(cr, 'project_timesheet_forecast_sale'):
        for field in fields:
            util.move_field_to_module(cr, 'project.forecast', field,
                                      'project_forecast', 'project_timesheet_forecast_sale')
    else:
        for field in fields:
            util.remove_field(cr, 'project.forecast', field)

    util.remove_record(cr, 'project_forecast.project_forecast_action_project')
