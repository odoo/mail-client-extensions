from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_translatable(cr, "hr.payroll.structure", "name")
    util.remove_field(cr, "res.config.settings", "group_payslip_display")

    util.create_column(cr, "hr_payslip_worked_days", "date_from", "date")
    util.create_column(cr, "hr_payslip_worked_days", "employee_id", "int4")
    query = """
        UPDATE hr_payslip_worked_days hpwd
           SET date_from = hp.date_from,
               employee_id = hp.employee_id
          FROM hr_payslip hp
         WHERE hpwd.payslip_id = hp.id
    """
    util.explode_execute(cr, query, table="hr_payslip_worked_days", alias="hpwd")
