# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "calendar.popover.delete.wizard.homework")
    util.remove_view(cr, "hr_homeworking.hr_employee_location_view_form")
    util.remove_field(cr, "hr.employee.location", "weekday")
    util.remove_field(cr, "hr.employee.location", "weekly")
    util.remove_field(cr, "hr.employee.location", "start_date")
    util.remove_field(cr, "hr.employee.location", "end_date_create")
    util.remove_field(cr, "hr.employee.location", "removed")
    util.remove_field(cr, "hr.employee.location", "parent_default_homeworking_id")
    util.remove_field(cr, "hr.employee.location", "child_removed_ids")
    util.remove_field(cr, "hr.employee.location", "current_location")
    util.remove_field(cr, "hr.employee.location", "end_date")
    util.remove_field(cr, "hr.employee.location", "today_next_date")

    # delete all created exceptions
    cr.execute("DELETE from hr_employee_location")

    home_office_wl = util.ref(cr, "hr.home_work_office")
    if home_office_wl:
        cr.execute(
            """
            UPDATE hr_employee
            SET monday_location_id = %(wl)s, tuesday_location_id = %(wl)s,
                wednesday_location_id = %(wl)s, thursday_location_id = %(wl)s,
                friday_location_id = %(wl)s, saturday_location_id = %(wl)s,
                sunday_location_id = %(wl)s
        """,
            {"wl": home_office_wl},
        )
