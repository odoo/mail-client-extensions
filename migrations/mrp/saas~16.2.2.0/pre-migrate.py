# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mrp_bom", "produce_delay", "double precision")
    util.create_column(cr, "mrp_bom", "days_to_prepare_mo", "double precision")
    query = """
        UPDATE mrp_bom b
           SET produce_delay = pt.produce_delay,
               days_to_prepare_mo = pt.days_to_prepare_mo
          FROM product_template pt
         WHERE b.product_tmpl_id = pt.id
           AND (pt.produce_delay <> 0 OR pt.days_to_prepare_mo <> 0)
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="mrp_bom", alias="b"))
    util.remove_field(cr, "product.template", "produce_delay")
    util.remove_field(cr, "product.template", "days_to_prepare_mo")
