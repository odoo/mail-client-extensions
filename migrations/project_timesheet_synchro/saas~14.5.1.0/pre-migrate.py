# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "project_timesheet_synchro.project_timesheet_synchro_app_action")
    util.remove_record(cr, "project_timesheet_synchro.menu_timesheet_app")
