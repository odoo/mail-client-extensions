# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE project_task
           SET progress = progress / 100
        """,
        table="project_task",
    )
    util.update_record_from_xml(cr, "base.module_category_services_timesheets", from_module="hr_timesheet")
