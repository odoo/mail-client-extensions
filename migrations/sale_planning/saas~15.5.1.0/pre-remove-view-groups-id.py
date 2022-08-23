# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_planning.planning_slot_view_form_inherit_sale_planning_salesman")
