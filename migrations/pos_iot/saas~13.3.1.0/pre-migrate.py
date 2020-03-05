# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "six_payment_terminal")
    util.remove_view(cr, "pos_iot.assets_backend")
    util.remove_view(cr, "pos_iot.pos_iot_session_view_form")
