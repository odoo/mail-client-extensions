# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE hr_payroll_employee_declaration
           SET state = CASE WHEN pdf_to_generate IS TRUE THEN 'pdf_to_generate'
                            WHEN pdf_file IS NOT NULL THEN 'pdf_generated'
                            ELSE 'draft' END
    """
    )
