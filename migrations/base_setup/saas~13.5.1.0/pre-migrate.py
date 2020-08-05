# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_config_settings", "module_microsoft_calendar", "boolean")
