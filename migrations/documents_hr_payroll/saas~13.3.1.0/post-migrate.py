# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        "UPDATE res_company SET documents_payroll_folder_id=%s WHERE documents_payroll_folder_id IS NULL",
        [util.ref(cr, "documents_hr_payroll.documents_payroll_folder")],
    )
