from odoo.upgrade import util


def migrate(cr, version):

    util.recompute_fields(cr, "hr.payslip", ["error_count", "warning_count", "issues"])

    query = """
        UPDATE hr_payslip
           SET state_display = CASE
                WHEN error_count > 0 THEN 'error'
                WHEN warning_count > 0 THEN 'warning'
                ELSE state END
    """
    util.explode_execute(cr, query, table="hr_payslip")
