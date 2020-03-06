# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.config", "is_installed_pos_iot")
    util.remove_column(cr, "pos_config", "module_pos_iot")
