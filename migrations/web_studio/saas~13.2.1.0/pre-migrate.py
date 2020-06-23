# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "ir_ui_menu", "is_studio_configuration", "boolean")
