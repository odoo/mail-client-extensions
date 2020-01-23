# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE hr_job DROP CONSTRAINT IF EXISTS hr_job_hired_employee_check")
