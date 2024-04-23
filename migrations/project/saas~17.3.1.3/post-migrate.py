from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "project.project_task_rule_portal", util.update_record_from_xml)
    util.if_unchanged(cr, "project.project_task_rule_portal_project_sharing", util.update_record_from_xml)
