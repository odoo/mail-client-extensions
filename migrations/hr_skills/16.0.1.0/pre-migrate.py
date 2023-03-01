# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "hr_employee_hr_skill_rel", "hr_employee", "hr_skill")
    # yes, this m2m is idiotic ¯\_(ツ)_/¯
    cr.execute(
        """
            INSERT into hr_employee_hr_skill_rel(hr_employee_id, hr_skill_id)
            SELECT DISTINCT employee_id, skill_id
              FROM hr_employee_skill
             WHERE employee_id IS NOT NULL
        """
    )
