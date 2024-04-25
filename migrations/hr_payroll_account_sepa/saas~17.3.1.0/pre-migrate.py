from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "hr.payslip.sepa.wizard")
    util.remove_model(cr, "hr.payslip.run.sepa.wizard")
