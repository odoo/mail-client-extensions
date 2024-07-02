from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_skills.action_hr_employee_skill_log_department")
    util.remove_record(cr, "hr_skills.hr_employee_skill_log_hr_user_rule")
    util.remove_record(cr, "hr_skills.hr_employee_skill_log_manager_rule")
