# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_maintenance.mrp_workorder_tablet_view_form_inherit_maintenance")
