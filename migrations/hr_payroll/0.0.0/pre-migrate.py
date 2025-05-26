import os

from odoo.addons.base.maintenance.migrations import util

ODOO_UPG_UPDATE_COMPANY_ID_ON_PAYSLIPS = util.str2bool(os.getenv("ODOO_UPG_UPDATE_COMPANY_ID_ON_PAYSLIPS", "0"))


def migrate(cr, version):
    if not util.version_between("17.0", "19.0"):
        return
    cr.execute(
        """
        SELECT slip.id,
               slip.name
          FROM hr_payslip slip
          JOIN hr_employee emp
            ON slip.employee_id = emp.id
         WHERE slip.company_id != emp.company_id
         LIMIT 50
        """
    )
    if not cr.rowcount:
        return
    payslip_links = " ".join(
        "<li>{}</li>".format(util.get_anchor_link_to_record("hr.payslip", slip_id, slip_name))
        for slip_id, slip_name in cr.fetchall()
    )
    if ODOO_UPG_UPDATE_COMPANY_ID_ON_PAYSLIPS:
        query = """
            UPDATE hr_payslip
               SET company_id = emp.company_id
              FROM hr_employee emp
             WHERE hr_payslip.employee_id = emp.id
               AND hr_payslip.company_id != emp.company_id
        """
        util.explode_execute(cr, query, table="hr_payslip")
        message = """
            <details>
                <summary>
                    <strong>Info:</strong> Payslips with mismatched company have been updated<br>

                    Some payslips had a company that did not match the employee's company.
                    They have been updated to match the employee's company.
                    This should resolve issues with payroll processing and reporting.
                    Below you can find a list of the updated payslip records.
                </summary>
                <ul>{}</ul>
            </details>
        """.format(payslip_links)
    else:
        message = """
            <details>
                <summary>
                    <strong>Warning:</strong> Some payslips have mismatched company<br>
                    They have a company that does not match the employee's company.

                    This may cause issues with payroll processing and reporting.
                    Below you can find a list of the affected records.
                    You can either fix them manually before the upgrade or,
                    choose to apply an automatic fix that will set the company
                    of the payslip to the one from the employee during the upgrade.

                    For the automatic fix, set the environment variable <code>ODOO_UPG_UPDATE_COMPANY_ID_ON_PAYSLIPS</code> to <code>1</code> and send a new upgrade request.
                </summary>
                <ul>{}</ul>
            </details>
        """.format(payslip_links)
    util.add_to_migration_reports(message=message, category="Payroll", format="html")
