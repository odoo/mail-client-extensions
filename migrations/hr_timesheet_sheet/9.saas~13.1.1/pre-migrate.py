# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_workflow(cr, 'hr_timesheet_sheet.sheet')

    sa = util.rename_xmlid(
        cr, *util.expand_braces('hr_timesheet_sheet.ir_actions_server_tim{,e}sheet_sheet'))
    if sa:
        cr.execute("""
            UPDATE ir_act_server
               SET code='action = env["hr.timesheet.current.open"].open_timesheet()'
             WHERE id=%s
        """, [sa])

    moved_fields = util.splitlines("""
        attendance_ids
        total_attendances
        total_timesheet
        total_difference
        period_ids
        attendance_count
    """)
    for f in moved_fields:
        util.move_field_to_module(cr, 'hr_timesheet_sheet.sheet', f,
                                  'hr_timesheet_sheet', 'hr_timesheet_attendance')
    util.remove_field(cr, 'hr_timesheet_sheet.sheet', 'state_attendance')
    util.move_field_to_module(cr, 'res.company', 'timesheet_max_difference',
                              'hr_timesheet_sheet', 'hr_timesheet_attendance')

    util.move_model(cr, 'hr_timesheet_sheet.sheet.day',
                    'hr_timesheet_sheet', 'hr_timesheet_attendance')

    xids_moved = util.splitlines("""
        access_hr_timesheet_sheet_sheet_day
        act_hr_timesheet_sheet_sheet_2_hr_attendance
        act_hr_timesheet_sheet_sheet_2_hr_analytic_timesheet

        view_hr_attendance_filter   hr_attendance_view_filter
        view_attendance_form        hr_attendance_view_form
        view_attendance_tree

        act_hr_timesheet_sheet_sheet_by_account
        act_hr_timesheet_sheet_sheet_by_day
        hr_timesheet_day_tree

    """)
    for x in xids_moved:
        if ' ' in x:
            f, t = x.split()
        else:
            f = t = x
        util.rename_xmlid(cr, 'hr_timesheet_sheet.' + f, 'hr_timesheet_attendance.' + t)

    util.remove_view(cr, 'hr_timesheet_sheet.hr_timesheet_sheet_company')
    util.remove_view(cr, 'hr_timesheet_sheet.view_attendance_tree_who')
