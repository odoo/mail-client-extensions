# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    payroll_folder = util.ref(cr, "documents_hr_payroll.documents_payroll_folder")

    cr.execute(
        "UPDATE res_company SET documents_payroll_folder_id=%s WHERE documents_payroll_folder_id IS NULL",
        [payroll_folder],
    )
    if cr.rowcount > 1:
        # if we are in multi-company
        # If the parent folder of "Payroll" is limited to a company, move "Payroll" at root
        cr.execute(
            """
                UPDATE documents_folder f
                   SET parent_folder_id = NULL
                  FROM documents_folder p
                 WHERE p.id = f.parent_folder_id
                   AND p.company_id IS NOT NULL
                   AND f.id = %s
            """,
            [payroll_folder],
        )
