# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "hr_leave_type", "validation_type", "varchar")
    util.create_column(cr, "hr_leave_type", "employee_applicability", "varchar")
    util.create_column(cr, "hr_leave_type", "validity_start", "date")
    util.create_column(cr, "hr_leave_type", "validity_stop", "date")
    util.create_column(cr, "hr_leave_type", "time_type", "varchar")
    util.create_column(cr, "hr_leave_type", "sequence", "integer")

    cr.execute(
        """
        UPDATE hr_leave_type
           SET validation_type = CASE WHEN double_validation THEN 'both'
                                      ELSE 'hr'
                                  END,
               employee_applicability = CASE WHEN "limit" THEN 'leave'
                                             ELSE 'both'
                                         END,
               time_type = 'leave',
               sequence = id
    """
    )

    for role in {"employee", "employee_write", "officer"}:
        for infix in {"rule{_request,}", "{rule_allocation,allocation_rule}"}:
            f, t = util.expand_braces(infix)
            util.rename_xmlid(
                cr,
                "hr_holidays.property_{}_{}".format(f, role),
                "hr_holidays.hr_leave_{}_{}".format(t, role),
            )

    # cleanup
    util.remove_field(cr, "hr.leave", "double_validation")
    util.remove_field(cr, "hr.leave.allocation", "double_validation")

    for prefix in {"", "department_"}:
        for infix in {"", "allocation_"}:
            for mt in {"confirmed", "first_validated"}:
                util.remove_record(cr, "hr_holidays.mt_{}leave_{}{}".format(prefix, infix, mt))
