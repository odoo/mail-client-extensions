# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, "hr_holidays.view_holiday_new_calendar", "hr_holidays.hr_leave_view_calendar")
    util.rename_xmlid(cr, "hr_holidays.view_holiday", "hr_holidays.hr_leave_view_tree", noupdate=False)
    cr.execute("UPDATE ir_act_window SET view_id=NULL, search_view_id=NULL WHERE id=%s",
               [util.ref(cr, "hr_holidays.action_hr_available_holidays_report")])
    views = util.splitlines("""
        edit_new_allocation
        view_allocation_tree
        hr_holidays_view_list_my_allocation

        view_holiday_status_tree
        view_hr_holidays_status_search

        edit_holiday_new_request

        view_allocation_tree_customize
        hr_holidays_leaves_assign_tree_view
    """)
    for view in views:
        util.remove_view(cr, "hr_holidays." + view)

    gone = util.splitlines("""
        action_open_allocation_tree
        action_open_allocation_form
        open_allocation

        action_request_approve_allocation_tree
        action_request_approve_allocation_form
        request_approve_allocation

        open_department_holidays_allocation_approve
        hr_holidays_action_allocation_from_department

        action_request_approve_holidays_tree
        action_request_approve_holidays_form
        request_approve_holidays

        menu_open_department_leave_allocation_approve
        menu_open_allocation

        action_open_ask_holidays_tree
        action_open_ask_holidays_form
        action_open_ask_holidays_calendar
        open_ask_holidays
        menu_open_ask_holidays_new

        open_employee_leaves
        menu_open_employee_leave
        open_department_holidays_approve
        menu_open_department_leave_approve

        act_hr_employee_holiday_request_approved
        hr_holidays_action_request_from_department

        action_hr_holidays_leaves_analysis
        action_hr_holidays_leaves_analysis_filtered
        action_window_leave_pivot

        act_hr_employee_holiday_request
        hr_holidays_leaves_assign_legal

    """)
    for x in gone:
        util.remove_record(cr, "hr_holidays." + x)
