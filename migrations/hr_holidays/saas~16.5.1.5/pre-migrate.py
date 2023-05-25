# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_holidays.menu_hr_holidays_{approvals,management}"))
    util.rename_model(cr, "hr.leave.stress.day", "hr.leave.mandatory.day")
    util.rename_field(cr, "hr.leave", "has_stress_day", "has_mandatory_day")

    rename_records = [
        "hr_holidays.hr_leave_stress_day_view_search",
        "hr_holidays.hr_leave_stress_day_view_list",
        "hr_holidays.hr_leave_stress_day_view_form",
        "hr_holidays.hr_leave_stress_day_rule_multi_company",
        "hr_holidays.hr_leave_stress_day_action",
        "hr_holidays.hr_leave_stress_day_1",
        "hr_holidays.hr_holidays_stress_day_menu_configuration",
        "hr_holidays.access_hr_leave_stress_day_manager",
        "hr_holidays.access_hr_leave_stress_day_user",
    ]

    for record in rename_records:
        util.rename_xmlid(cr, record, record.replace("stress", "mandatory"))
