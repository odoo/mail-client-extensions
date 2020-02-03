# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "email_sent", "boolean")
    util.create_column(cr, "hr_employee", "ip_connected", "boolean")
    util.create_column(cr, "hr_employee", "manually_set_present", "boolean")
    # column `hr_presence_state_display` has been renamed in `hr` script

    util.remove_view(cr, "hr_presence.hr_employee_view_form")
    util.remove_view(cr, "hr_presence.hr_employee_view_kanban_inherit")
