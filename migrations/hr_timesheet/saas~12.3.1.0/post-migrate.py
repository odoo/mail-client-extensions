# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "hr_timesheet.group_hr_timesheet_user", noupdate=True)
