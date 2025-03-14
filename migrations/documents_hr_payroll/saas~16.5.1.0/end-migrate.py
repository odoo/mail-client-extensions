def migrate(cr, version):
    cr.execute(
        """
        UPDATE hr_payroll_employee_declaration
           SET state = 'pdf_to_post'
         WHERE pdf_to_post IS TRUE
    """
    )
