# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp.mrp_production_workorder_form_view_inherit_gantt")
    # remove mail.thread and mail.activity.mixin inheritance
    util.remove_inherit_from_model(cr, 'mrp.workorder', 'mail.thread')
    util.remove_inherit_from_model(cr, 'mrp.workorder', 'mail.activity.mixin')
