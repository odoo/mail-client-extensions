# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    toremove = util.splitlines("""
        action_generate_forecast
        project_forecast_server_action_archive

        action_project_forecast_grid_by_user
        action_project_forecast_grid_by_project
        project_forecast_action_from_task

        menu_project_forecast_grid_by_user
        menu_project_forecast_grid_by_project
        menu_project_forecast_grid
    """)
    for r in toremove:
        util.remove_record(cr, 'project_forecast.' + r)

    views = util.splitlines("""
        project_forecast_grid
        view_project_set_dates
        task_view_form_inherit_project_forecast
    """)
    for v in views:
        util.remove_view(cr, 'project_forecast.' + v)

    util.create_column(cr, 'project_forecast', 'company_id', 'int4')
    cr.execute("DELETE FROM project_forecast WHERE project_id IS NULL")
    cr.execute("""
        UPDATE project_forecast f
           SET company_id = a.company_id
          FROM project_project p
          JOIN account_analytic_account a ON (a.id = p.analytic_account_id)
         WHERE p.id = f.project_id
    """)

    util.create_column(cr, 'res_company', 'forecast_uom', 'varchar')
    util.create_column(cr, 'res_company', 'forecast_span', 'varchar')
    cr.execute("UPDATE res_company SET forecast_uom='day', forecast_span='month'")

    util.remove_model(cr, 'project.forecast.assignment')
