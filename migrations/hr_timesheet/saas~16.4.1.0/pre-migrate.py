# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_timesheet.rating_rating_view_search_project_inherited")
