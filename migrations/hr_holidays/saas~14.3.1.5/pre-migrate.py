# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.employee.base", "current_leave_id", skip_inherit=("hr.employee",))
