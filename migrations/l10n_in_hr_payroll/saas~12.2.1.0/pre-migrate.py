# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "payment.advice.report")
    util.remove_model(cr, "payslip.report")

    menus = util.splitlines(
        """
        menu_l10n_in_hr_payroll_report
        menu_reporting_payment_advice
        menu_reporting_payslip
    """
    )
    util.remove_menus(cr, [util.ref(cr, "l10n_in_hr_payroll." + m) for m in menus])

    util.remove_view(cr, "l10n_in_hr_payroll.hr_department_view_kanban")
