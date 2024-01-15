# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rt = {"reset_translations": {"subject", "body_html"}}

    util.update_record_from_xml(cr, "project.task_visibility_rule")
    util.if_unchanged(cr, "project.mail_template_data_project_task", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "project.rating_project_request_email_template", util.update_record_from_xml, **rt)
