# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "hr_leave_type", "create_calendar_meeting", "boolean")
    cr.execute("UPDATE hr_leave_type SET create_calendar_meeting=TRUE WHERE categ_id IS NOT NULL")
    util.remove_field(cr, "hr.leave.type", "categ_id")
