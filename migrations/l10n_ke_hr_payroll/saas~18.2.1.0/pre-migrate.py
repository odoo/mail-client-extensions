from odoo.upgrade import util

def migrate(cr, version):
    util.remove_model(cr, "l10n.ke.hr.payroll.nhif.report.line.wizard")
    util.remove_model(cr, "l10n.ke.hr.payroll.nhif.report.wizard")
