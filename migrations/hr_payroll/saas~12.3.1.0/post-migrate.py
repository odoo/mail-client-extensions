# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_payroll.group_hr_payroll_user")
    util.update_record_from_xml(cr, "hr_payroll.group_hr_payroll_manager")

    type_id = util.ref(cr, "hr_payroll.structure_type_employee")
    if not type_id:
        # Since saas~12.5, default type "employee" as been moved to demo data. See odoo/enterprise#4584
        type_id = (
            util.env(cr)["hr.payroll.structure.type"]
            .create({"name": "Employee", "country_id": False})
            .id
        )

    cr.execute("UPDATE hr_payroll_structure SET type_id=%s WHERE type_id IS NULL", [type_id])
    cr.execute('ALTER TABLE "hr_payroll_structure" ALTER COLUMN "type_id" SET NOT NULL')
