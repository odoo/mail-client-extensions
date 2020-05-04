# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for model in {"leave", "leave_allocation", "department_leave", "department_leave_allocation"}:
        for action in {"approved", "refused"}:
            util.remove_record(cr, "hr_holidays.mt_{}_{}".format(model, action))

    util.create_column(cr, "hr_employee", "leave_manager_id", "int4")

    for suffix in {"from", "to"}:
        cr.execute("""
            ALTER TABLE hr_leave
            ALTER COLUMN request_hour_{0}
                    TYPE varchar
                   USING CASE WHEN request_hour_{0} >= 0
                              THEN request_hour_{0}::varchar
                              ELSE (abs(request_hour_{0}) - 0.5)::varchar
                          END
        """.format(suffix))

    util.create_column(cr, "hr_leave_allocation", "manager_id", "int4")
    # we cannot set *current* employee manager as the manager on all allocations because
    # employee may have change manager at time the allocation was created.
    # leave it empty

    util.remove_field(cr, "hr.leave.type", "double_validation")

    util.rename_field(cr, "hr.leave.report", "type", "leave_type")

    util.rename_xmlid(cr, *util.expand_braces("hr_holidays.resource_leaves_{officer,team_leader}"))
