# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "project.project_manager_all_project_tasks_rule")

    cr.execute(
        """
        UPDATE project_task_type
           SET fold=true
         WHERE is_closed=true
           AND fold=false
    """
    )
    util.update_field_usage(cr, "project.task.type", "is_closed", "fold")
    util.remove_field(cr, "project.task.type", "is_closed")
