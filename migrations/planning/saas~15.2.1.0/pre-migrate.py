# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "planning.view_employee_tree_inherit_planning")
    util.remove_view(cr, "planning.view_employee_public_tree_inherit_planning")
