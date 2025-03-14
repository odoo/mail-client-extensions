from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "planning_hr_skills.planning_analysis_report_view_search")
