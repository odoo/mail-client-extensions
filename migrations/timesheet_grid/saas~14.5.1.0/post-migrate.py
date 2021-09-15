# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "timesheet_grid.mail_template_timesheet_reminder_user", util.update_record_from_xml)
    util.if_unchanged(cr, "timesheet_grid.mail_template_timesheet_reminder_manager", util.update_record_from_xml)
