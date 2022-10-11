# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.workorder", "ip")
    util.remove_field(cr, "mrp.workorder", "identifier")
    util.remove_field(cr, "mrp.workorder", "boxes")
    util.remove_field(cr, "mrp.workorder", "device_name")

    util.remove_view(cr, "mrp_workorder_iot.mrp_workorder_view_form_iot_inherit_quality")
