# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'project.project', 'alias_model')

    util.create_column(cr, 'project_task', 'email_from', 'varchar')
    util.create_column(cr, 'project_task', 'email_cc', 'varchar')

    util.create_column(cr, 'project_task', 'working_hours_open', 'float8')
    util.create_column(cr, 'project_task', 'working_hours_close', 'float8')
    util.create_column(cr, 'project_task', 'working_days_open', 'float8')
    util.create_column(cr, 'project_task', 'working_days_close', 'float8')
    # these working_* fields will (maybe) computed in post- script, once issues have been converted to tasks

    util.remove_field(cr, 'account.analytic.account', 'use_tasks')
