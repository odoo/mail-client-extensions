# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, xml_id="mrp_plm.mrp_bom_view_kanban")

    util.remove_field(cr, "mrp.bom", "revision_ids")
