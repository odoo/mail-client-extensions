# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "planning.slot", "allocated_hours_cost")
    util.remove_field(cr, "planning.slot", "effective_hours_cost")
