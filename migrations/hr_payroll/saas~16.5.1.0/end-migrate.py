from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE hr_payroll_employee_declaration
           SET state = CASE WHEN pdf_to_generate IS TRUE THEN 'pdf_to_generate'
                            WHEN pdf_file IS NOT NULL THEN 'pdf_generated'
                            ELSE 'draft' END
    """
    )

    cr.execute(
        r"""
        SELECT
               r.id,
               r.name->>'en_US'
          FROM hr_salary_rule r
         WHERE
               CONCAT(
                    r.amount_python_compute,
                    r.quantity,
                    r.amount_percentage_base,
                    r.condition_range,
                    r.condition_python
                ) ~ ANY (ARRAY['\ycategories\.(?!get\()\w', '\yinputs\.(?!get\()\w', '\yworked_days\.(?!get\()\w', '\yrules\.(?!get\()\w'])
        """
    )
    if cr.rowcount:
        msg = """
            <details>
              <summary>
                The following payroll salary rules have to be updated because browsable objects
                no longer exist. For instance "result = inputs.SALARY and inputs.SALARY.amount"
                would become "result = 'SALARY' in inputs and inputs['SALARY'].amount".
              </summary>
              <ul>{}</ul>
            </details>
        """.format(
            "".join(f"<li>{util.get_anchor_link_to_record('hr.salary.rule', *rule)}</li>" for rule in cr.fetchall())
        )
        util.add_to_migration_reports(msg, "Payroll", format="html")
