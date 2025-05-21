from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_skills_survey.hr_resume_line_view_search")
    util.remove_view(cr, "hr_skills_survey.hr_employee_certification_report_view_list")
    util.remove_record(cr, "hr_skills_survey.hr_employee_certification_report_action")
    util.remove_menus(cr, [util.ref(cr, "hr_skills_survey.hr_employee_certication_report_menu")])
