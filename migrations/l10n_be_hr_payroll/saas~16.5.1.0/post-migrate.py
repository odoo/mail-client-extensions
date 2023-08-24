# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    pdf_to_post = ", pdf_to_post" if util.modules_installed(cr, "documents_l10n_be_hr_payroll") else ""
    for declaration_model in ["l10n_be_individual_account", "l10n_be_281_10", "l10n_be_281_45"]:
        declaration_line_model = f"{declaration_model}_line"
        cr.execute(
            f"""
            INSERT INTO hr_payroll_employee_declaration (
                create_uid,
                create_date,
                write_uid,
                write_date,
                res_id,
                employee_id,
                company_id,
                res_model,
                pdf_filename,
                pdf_to_generate,
                pdf_file
                {pdf_to_post}
            )
            SELECT
                dlm.create_uid,
                dlm.create_date,
                dlm.write_uid,
                dlm.write_date,
                sheet_id,
                employee_id,
                dm.company_id,
                'l10n_be.individual.account',
                pdf_filename,
                pdf_to_generate,
                pdf_file
                {pdf_to_post}
            FROM {declaration_line_model} dlm
            JOIN {declaration_model} dm
            ON dlm.sheet_id = dm.id
            """
        )

    cr.execute("DROP TABLE l10n_be_individual_account_line")
    cr.execute("DROP TABLE l10n_be_281_10_line")
    cr.execute("DROP TABLE l10n_be_281_45_line")
