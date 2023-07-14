# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mrp_workorder", "barcode", "varchar")
    query = """
    UPDATE mrp_workorder mw
       SET barcode = CONCAT(mp.name, '/', mw.id)
      FROM mrp_production mp
     WHERE mw.production_id = mp.id
    """
    util.explode_execute(cr, query, table="mrp_workorder", alias="mw")
    util.remove_field(cr, "res.config.settings", "module_mrp_workorder")
