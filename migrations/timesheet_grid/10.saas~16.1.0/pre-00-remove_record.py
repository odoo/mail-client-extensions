# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'timesheet_grid.menu_timesheet_grid_my')
    util.remove_record(cr, 'timesheet_grid.menu_timesheet_grid_all')

    util.rename_model(cr, 'timesheet_grid.validable', 'timesheet.validation.line')
    util.rename_model(cr, 'timesheet_grid.validation', 'timesheet.validation')

    util.rename_field(cr, 'timesheet.validation', 'validation_to', 'validation_date')
    util.rename_field(cr, 'timesheet.validation', 'validable_ids', 'validation_line_ids')

    util.rename_xmlid(cr, 'timesheet_grid.view_timesheet_form', 'timesheet_grid.timesheet_view_form')
    util.rename_xmlid(cr, 'timesheet_grid.view_timesheet_grid', 'timesheet_grid.timesheet_view_grid_by_project')
    util.rename_xmlid(cr, 'timesheet_grid.view_timesheet_grid_readonly', 'timesheet_grid.timesheet_view_grid_by_project_readonly')

    util.remove_view(cr, 'timesheet_grid.view_timesheet_list')
    util.remove_view(cr, 'timesheet_grid.view_timesheet_grid_validate')
    util.remove_view(cr, 'timesheet_grid.view_timesheet_grid_search')
    util.remove_view(cr, 'timesheet_grid.view_timesheet_grid_validation_search')
    util.remove_view(cr, 'timesheet_grid.hr_timesheet_employee_form_validation')
    util.remove_view(cr, 'timesheet_grid.view_timesheet_search')
    util.remove_view(cr, 'timesheet_grid.validable_form')

    cr.execute("DELETE FROM ir_act_window_view WHERE act_window_id in %s",
               [(util.ref(cr, 'timesheet_grid.action_timesheet_previous_week'),
                 util.ref(cr, 'timesheet_grid.action_timesheet_previous_month'),)
               ])

    actions = [
        'action_timesheet_current', 'action_timesheet_all', 'act_hr_timesheet_line_grid'
    ]
    for action in actions:
        util.remove_record(cr, 'timesheet_grid.' + action)
