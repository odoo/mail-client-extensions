# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(cr, "UPDATE hr_leave SET state = 'cancel' WHERE active = False", "hr_leave")

    util.explode_execute(
        cr,
        """
        UPDATE hr_leave_allocation a
           SET date_to = COALESCE(e.departure_date, CURRENT_DATE)
          FROM hr_employee e
         WHERE a.employee_id = e.id
           AND a.active = False
        """,
        "hr_leave_allocation",
        alias="a",
    )

    def leave_domain_adapter(leaf, _or, _neg):
        _, op, right = leaf
        new_op = "!=" if (op == "=" and right) or (op == "!=" and not right) else "="
        return [("state", new_op, "cancel")]

    util.adapt_domains(cr, "hr.leave", "active", "state", adapter=leave_domain_adapter)

    util.remove_field(cr, "hr.leave", "active")
    util.remove_field(cr, "hr.leave.allocation", "active")

    util.remove_field(cr, "hr.departure.wizard", "archive_allocation")
    util.remove_field(cr, "hr.departure.wizard", "cancel_leaves")

    util.remove_view(cr, "hr_holidays.hr_departure_wizard_view_form")
    util.remove_view(cr, "hr_holidays.hr_leave_report_search_view")
