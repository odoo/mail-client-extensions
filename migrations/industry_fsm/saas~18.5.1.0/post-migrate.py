from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "industry_fsm.report_project_task_user_fsm_rule")
