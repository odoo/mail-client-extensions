# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_run_tree")
