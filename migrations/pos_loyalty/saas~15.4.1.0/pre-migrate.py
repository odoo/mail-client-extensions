# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_loyalty.pos_config_view_form_inherit_pos_loyalty")
