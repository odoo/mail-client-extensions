# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "project.project_public_members_rule")
    util.update_record_from_xml(cr, "project.task_visibility_rule")
    util.update_record_from_xml(cr, "project.project_project_rule_portal")
    util.update_record_from_xml(cr, "project.project_task_rule_portal")
