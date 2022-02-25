# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "planning_holidays.planning_slot_view_search_inherit_planning_holidays")
