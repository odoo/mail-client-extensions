# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.remove_field(cr, "hr.employee.base", "allocation_used_display")
    util.remove_field(cr, "hr.employee.base", "allocation_used_count")

    util.remove_field(cr, "res.users", "allocation_used_display")
    util.remove_field(cr, "res.users", "allocation_used_count")

    util.rename_field(cr, "hr.leave.type", "group_days_allocation", "allocation_count")
