# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    pdf_to_post = ", pdf_to_post" if util.modules_installed(cr, "documents_l10n_be_hr_payroll") else ""

    for declaration_model in ["l10n_be.individual.account", "l10n_be.281_10", "l10n_be.281_45"]:
        declaration_table = util.table_of_model(cr, declaration_model)
        declaration_line_table = f"{declaration_table}_line"
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
                l.create_uid,
                l.create_date,
                l.write_uid,
                l.write_date,
                l.sheet_id,
                l.employee_id,
                d.company_id,
                %s,
                l.pdf_filename,
                l.pdf_to_generate,
                l.pdf_file
                {pdf_to_post}
            FROM {declaration_line_table} l
            JOIN {declaration_table} d
              ON l.sheet_id = d.id
            """,
            [declaration_model],
        )

    cr.execute("DROP TABLE l10n_be_individual_account_line")
    cr.execute("DROP TABLE l10n_be_281_10_line")
    cr.execute("DROP TABLE l10n_be_281_45_line")
