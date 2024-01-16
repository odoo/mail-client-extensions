# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "project.project_manager_all_project_tasks_rule")
