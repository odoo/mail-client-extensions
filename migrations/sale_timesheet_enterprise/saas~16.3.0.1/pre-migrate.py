# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet_enterprise.timesheet_view_tree_inherit")
