# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rules = """
        project_public_members_rule
        task_visibility_rule
        project_project_rule_portal
        project_task_rule_portal
    """
    for rule in util.splitlines(rules):
        util.update_record_from_xml(cr, f"project.{rule}")
