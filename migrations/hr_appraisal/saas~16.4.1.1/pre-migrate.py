from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.appraisal.goal", "is_implicit_manager")
    util.remove_field(cr, "hr.appraisal", "is_appraisal_manager")
    util.remove_field(cr, "hr.appraisal", "is_implicit_manager")
