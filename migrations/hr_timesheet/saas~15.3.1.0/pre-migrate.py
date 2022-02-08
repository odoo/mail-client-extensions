# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_timesheet.project_sharing_inherit_project_task_view_search")
