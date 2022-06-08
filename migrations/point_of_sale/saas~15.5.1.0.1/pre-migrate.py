# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.config", "barcode_nomenclature_id")
    util.remove_field(cr, "res.config.settings", "pos_barcode_nomenclature_id")
