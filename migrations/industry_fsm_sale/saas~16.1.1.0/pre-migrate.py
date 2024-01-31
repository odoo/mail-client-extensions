from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "industry_fsm_sale.field_service_project_stage_0")
    util.if_unchanged(cr, "industry_fsm.fsm_project", util.update_record_from_xml, force_create=True)
    util.remove_view(cr, "industry_fsm_sale.report_project_task_user_fsm_view_search_inherit_sale")
