# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "point_of_sale.FieldTextHtml")
    util.remove_view(cr, "point_of_sale.pos_editor_fieldtexthtml_assets")
