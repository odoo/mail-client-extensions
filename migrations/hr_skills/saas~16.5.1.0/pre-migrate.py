from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_skills.action_open_skills_log_employee")
