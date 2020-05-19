# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, "point_of_sale.view_pos_config_form", "point_of_sale.pos_config_view_form")
