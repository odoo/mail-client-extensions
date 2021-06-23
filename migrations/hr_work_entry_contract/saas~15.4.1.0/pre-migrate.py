# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract", "last_generation_date", "timestamp")
    util.create_column(cr, "hr_contract", "work_entry_source", "varchar", default="calendar")
