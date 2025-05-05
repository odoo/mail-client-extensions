from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "project.project_public_members_rule")
    util.update_record_from_xml(cr, "project.task_visibility_rule")
    util.update_record_from_xml(cr, "project.task_visibility_rule_project_user")
    util.update_record_from_xml(cr, "project.ir_rule_private_task")
    util.update_record_from_xml(cr, "project.project_project_rule_portal")
    util.update_record_from_xml(cr, "project.project_collaborator_rule_portal")
    util.update_record_from_xml(cr, "project.project_task_rule_portal")
    util.update_record_from_xml(cr, "project.project_task_rule_portal_project_sharing")
    util.update_record_from_xml(cr, "project.update_visibility_rule")
    util.update_record_from_xml(cr, "project.report_project_task_user_rule")
    util.update_record_from_xml(cr, "project.burndown_chart_project_user_rule")
    util.update_record_from_xml(cr, "project.milestone_visibility_rule")
    util.update_record_from_xml(cr, "project.project_milestone_rule_portal_project_sharing")
    util.if_unchanged(cr, "project.rating_project_request_email_template", util.update_record_from_xml)
    util.update_record_from_xml(cr, "project.ir_cron_rating_project")
