# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Some customers may have use data from `pos_data_drinks` module.
    # In this case, we cannot remove all data inconditionnaly.

    sub = " UNION ".join(['SELECT 1 FROM "{}" x WHERE x.{}=t.id'.format(f[0], f[1])
                          for f in util.get_fk(cr, "product_product")])

    if sub:
        cr.execute("""
            UPDATE ir_model_data
               SET module = 'point_of_sale',
                   name = 'pos_data_drinks_' || name,
                   noupdate = true
             WHERE module = 'pos_data_drinks'
               AND EXISTS(
                    SELECT 1
                      FROM product_product t
                     WHERE id IN (SELECT res_id
                                    FROM ir_model_data
                                   WHERE module = 'pos_data_drinks'
                                     AND model = 'product.product')
                       AND EXISTS({})
                   )
        """.format(sub))

    util.remove_module(cr, "pos_data_drinks")
