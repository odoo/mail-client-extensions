from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_appraisal.hr_appraisal_manager_feedback")
    util.remove_view(cr, "hr_appraisal.hr_appraisal_employee_feedback")
