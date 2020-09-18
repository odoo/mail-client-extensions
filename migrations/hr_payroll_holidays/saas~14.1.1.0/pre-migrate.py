# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_leave", "to_defer", "boolean")
    util.create_column(cr, "res_company", "deferred_time_off_manager", "int4")
