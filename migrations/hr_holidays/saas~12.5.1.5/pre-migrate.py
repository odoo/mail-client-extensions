# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr.leave", "out_of_office_message")

    util.create_column(cr, "hr_leave_allocation", "allocation_type", "varchar")
    cr.execute(
        """
        UPDATE hr_leave_allocation
           SET allocation_type = CASE accrual WHEN true THEN 'accrual' ELSE 'regular' END
    """
    )
    util.remove_field(cr, "hr.leave.allocation", "accrual")

    # same name, different model; remove the existing one
    util.remove_record(cr, "hr_holidays.act_hr_employee_holiday_request")

    util.remove_record(cr, "hr_holidays.group_hr_holidays_team_leader")
    util.remove_record(cr, "hr_holidays.hr_leave_rule_team_leader_update")
    util.remove_record(cr, "hr_holidays.hr_leave_allocation_rule_team_leader")
    util.remove_record(cr, "hr_holidays.resource_leaves_team_leader")

    util.remove_model(cr, "hr.holidays.summary.dept")
    util.remove_record(cr, "hr_holidays.menu_hr_holidays_summary_dept")
