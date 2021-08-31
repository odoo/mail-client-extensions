# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_payroll_holidays.hr_leave_view_{form,search}"))

    # Create Columns
    util.create_column(cr, "hr_leave", "payslip_state", "varchar", default="normal")

    # Remove Views
    util.remove_view(cr, "hr_payroll_holidays.hr_leave_view_form")

    # compute payslip state
    cr.execute(
        """
        UPDATE hr_leave leave
           SET payslip_state=(CASE
                WHEN payslip_status IS TRUE THEN 'done'
                WHEN to_defer IS TRUE THEN 'blocked'
            END)
         WHERE leave.payslip_status IS TRUE
            OR leave.to_defer IS TRUE
    """
    )

    # Remove fields
    util.remove_field(cr, "hr.leave", "to_defer")
    util.remove_column(cr, "hr_leave", "payslip_status")
