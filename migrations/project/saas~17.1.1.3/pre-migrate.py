# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project.personal_task_type_edit")
    util.update_record_from_xml(cr, "base.module_category_services_project", from_module="project")
