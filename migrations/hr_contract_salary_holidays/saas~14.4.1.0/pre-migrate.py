# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, 'hr_contract', 'leave_allocation_id', 'int4')
