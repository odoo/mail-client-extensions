# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DROP TABLE hr_analytic_timesheet CASCADE")
