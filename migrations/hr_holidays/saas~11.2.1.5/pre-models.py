# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces

    util.rename_model(cr, 'hr.holidays.status', 'hr.leave.type')
    util.rename_model(cr, 'hr.holidays', 'hr.leave')
    util.remove_model(cr, 'hr.holidays.remaining.leaves.user')

    renames = util.splitlines("""
        # message types
        hr_holidays.mt_{holidays,leave}_confirmed
        hr_holidays.mt_{holidays,leave}_first_validated
        hr_holidays.mt_{holidays,leave}_approved
        hr_holidays.mt_{holidays,leave}_refused
        hr_holidays.mt_department_{holidays,leave}_confirmed
        hr_holidays.mt_department_{holidays,leave}_first_validated
        hr_holidays.mt_department_{holidays,leave}_approved
        hr_holidays.mt_department_{holidays,leave}_refused

        # rules
        property_rule_{holidays,request}_employee
        property_rule_{holidays,request}_employee_write
        property_rule_{holidays,request}_officer

        # access
        access_hr_holidays_user{,_request}
        access_hr_holidays_employee{,_request}

        # stupid typo
        access_hr_hol{y,i}days_status_employee
        access_hr_hol{y,i}days_status_manager

        # views
        edit_holiday_new{,_request}
        view_{holiday_,}allocation_tree
        view_{holiday_,}allocation_tree_customize
    """)
    for r in renames:
        util.rename_xmlid(cr, *eb('hr_holidays.' + r))

    views = util.splitlines("""
        view_holiday_simple
        view_hr_holidays_kanban
    """)
    for v in views:
        util.remove_view(cr, 'hr_holidays.' + v)
