# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "planning.planning_filter_by_employee")
