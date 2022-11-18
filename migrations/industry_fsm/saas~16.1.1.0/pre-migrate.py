from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "industry_fsm.view_project_project_filter_inherit_industry_fsm")
    util.remove_field(cr, "report.project.task.user.fsm", "fsm_done")
