from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "project.mail_template_data_project_task", util.update_record_from_xml)
    util.if_unchanged(cr, "project.project_task_rule_portal", util.update_record_from_xml)
    util.if_unchanged(cr, "project.mt_task_canceled", util.update_record_from_xml)
