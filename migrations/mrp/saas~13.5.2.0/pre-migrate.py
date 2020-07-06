# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp.mrp_production_workorder_form_view_inherit_gantt")
