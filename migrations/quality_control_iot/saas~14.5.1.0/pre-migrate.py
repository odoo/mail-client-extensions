# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "quality_control_iot.quality_check_view_form_small_inherit")
