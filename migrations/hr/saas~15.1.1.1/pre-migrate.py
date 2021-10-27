# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "resource.resource", "employee_id", "planning", "hr")
