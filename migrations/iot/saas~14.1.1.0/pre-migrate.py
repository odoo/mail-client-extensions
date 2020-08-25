# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "iot.box", "screen_url")
    util.rename_field(cr, "iot.device", "screen_url", "display_url")
