# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_constraint(cr, "hr_job", "hr_job_hired_employee_check")
