# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_payroll.hr_rule_parameter_value_view_form")

    cr.execute(
        """
        UPDATE hr_payroll_structure_type pst
           SET name = initcap(wage_type || ' fixed wage paid ' || default_schedule_pay)
         WHERE pst.name IS NULL
    """
    )
