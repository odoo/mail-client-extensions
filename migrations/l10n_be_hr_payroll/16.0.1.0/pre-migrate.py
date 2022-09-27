# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # removed view
    util.remove_view(cr, "l10n_be_hr_payroll.contract_employee_report_view_dashboard_inherit")
