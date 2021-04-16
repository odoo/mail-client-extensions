# -*- coding: utf-8 -*-
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
