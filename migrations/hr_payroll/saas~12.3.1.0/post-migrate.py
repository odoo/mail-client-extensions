# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.update_record_from_xml(cr, 'hr_payroll.group_hr_payroll_user')
    util.update_record_from_xml(cr, 'hr_payroll.group_hr_payroll_manager')
    cr.execute(
        "UPDATE hr_payroll_structure SET type_id=%s",
        [util.ref(cr, "hr_payroll.structure_type_employee")],
    )
    cr.execute('ALTER TABLE "hr_payroll_structure" ALTER COLUMN "type_id" SET NOT NULL')
