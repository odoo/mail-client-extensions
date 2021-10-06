# -*- coding: utf-8 -*-
from psycopg2.extras import execute_values

from odoo.upgrade import util


def migrate(cr, version):

    # We add 2 basic rules on all the existing structures
    deduction_categ_id = util.ref(cr, "hr_payroll.DED")
    allowance_categ_id = util.ref(cr, "hr_payroll.ALW")

    cr.execute("SELECT id FROM hr_payroll_structure")
    structure_ids = [s["id"] for s in cr.dictfetchall()]

    values = []
    for structure_id in structure_ids:
        values.append(
            (
                structure_id,
                "Deduction",
                198,
                "DEDUCTION",
                deduction_categ_id,
                "python",
                "result = inputs.DEDUCTION",
                "code",
                "result = -inputs.DEDUCTION.amount",
                1,
                True,
                True,
            )
        )
        values.append(
            (
                structure_id,
                "Reimbursement",
                199,
                "REIMBURSEMENT",
                allowance_categ_id,
                "python",
                "result = inputs.REIMBURSEMENT",
                "code",
                "result = inputs.REIMBURSEMENT.amount",
                1,
                True,
                True,
            )
        )

    execute_values(
        cr._obj,
        """
        INSERT INTO
            hr_salary_rule(
                struct_id,
                name,
                sequence,
                code,
                category_id,
                condition_select,
                condition_python,
                amount_select,
                amount_python_compute,
                quantity,
                active,
                appears_on_payslip
            )
        VALUES %s""",
        values,
    )
