from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("CREATE TABLE hr_salary_attachment(id SERIAL NOT NULL, PRIMARY KEY(id))")
    util.create_m2m(cr, "hr_payslip_hr_salary_attachment_rel", "hr_payslip", "hr_salary_attachment")
