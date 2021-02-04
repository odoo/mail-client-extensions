# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    util.recompute_fields(cr, "mrp.eco", ["routing_change_ids", "bom_change_ids"])
