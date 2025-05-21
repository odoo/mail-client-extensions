from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.appraisal.skill", "employee_skill_id")
    util.rename_field(cr, "hr.appraisal", "skill_ids", "appraisal_skill_ids")
