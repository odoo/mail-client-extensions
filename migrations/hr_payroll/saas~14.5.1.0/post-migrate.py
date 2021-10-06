# -*- coding: utf-8 -*-
from psycopg2.extras import execute_values

from odoo.upgrade import util


def migrate(cr, version):
    if util.table_exists(cr, "l10n_be_attachment_salary"):
        # Try to migrate everything from l10n_be_attachment_salary but ignore those that miss information
        cr.execute(
            """
    INSERT INTO hr_salary_attachment(
                employee_id, company_id, description, deduction_type, monthly_amount,
                total_amount, paid_amount, date_start, date_end, state,
                create_uid, create_date, write_uid, write_date)
         SELECT c.employee_id,
                c.company_id,
                COALESCE(s.name, 'No description') AS description,
                (CASE s.garnished_type
                    WHEN 'attachment_salary' THEN 'attachment'
                    WHEN 'assignment_salary' THEN 'assignment'
                    ELSE s.garnished_type
                END) AS deduction_type,
                s.amount AS monthly_amount,
                (CASE
                    WHEN s.date_to IS NOT NULL THEN (
                            (DATE_PART('year', s.date_to) - DATE_PART('year', s.date_from)) * 12 +
                                (DATE_PART('month', s.date_to) - DATE_PART('month', s.date_from) + 1)
                        ) * s.amount
                    ELSE 0
                END) AS total_amount,
                (
                    (DATE_PART('year', least(s.date_to, CURRENT_DATE)) - DATE_PART('year', s.date_from)) * 12 +
                    (DATE_PART('month', least(s.date_to, CURRENT_DATE)) - DATE_PART('month', s.date_from) + 1)
                ) * s.amount AS paid_amount,
                s.date_from AS date_start,
                CASE WHEN s.date_to < CURRENT_DATE THEN s.date_to ELSE NULL END AS date_end,
                CASE WHEN s.date_to < CURRENT_DATE THEN 'close' ELSE 'open' END as state,
                s.create_uid,
                s.create_date,
                s.write_uid,
                s.write_date
           FROM l10n_be_attachment_salary s
           JOIN hr_contract c ON s.contract_id=c.id
          WHERE s.date_from IS NOT NULL AND s.contract_id IS NOT NULL
            """
        )

    # We add 3 basic rules on all the existing structures
    deduction_categ_id = util.ref(cr, "hr_payroll.DED")

    cr.execute("SELECT id FROM hr_payroll_structure")
    structure_ids = [s["id"] for s in cr.dictfetchall()]

    values = []
    for structure_id in structure_ids:
        values.append(
            (
                structure_id,
                "Attachment of Salary",
                174,
                "ATTACH_SALARY",
                deduction_categ_id,
                "python",
                "result = inputs.ATTACH_SALARY",
                "code",
                """result = -inputs.ATTACH_SALARY.amount
result_name = inputs.ATTACH_SALARY.name""",
                1,
                True,
                True,
            )
        )
        values.append(
            (
                structure_id,
                "Assignment of Salary",
                174,
                "ASSIG_SALARY",
                deduction_categ_id,
                "python",
                "result = inputs.ASSIG_SALARY",
                "code",
                """result = -inputs.ASSIG_SALARY.amount
result_name = inputs.ASSIG_SALARY.name""",
                1,
                True,
                True,
            )
        )
        values.append(
            (
                structure_id,
                "Child Support",
                174,
                "CHILD_SUPPORT",
                deduction_categ_id,
                "python",
                "result = inputs.CHILD_SUPPORT",
                "code",
                """result = -inputs.CHILD_SUPPORT.amount
result_name = inputs.CHILD_SUPPORT.name""",
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
