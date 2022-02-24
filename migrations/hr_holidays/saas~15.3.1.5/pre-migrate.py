# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "hr.leave.type", "allocation_validation_type", {"set": "officer"})
    util.remove_field(cr, "hr.leave.accrual.level", "level")
