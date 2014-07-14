# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.create_column(cr, "product_template", 'sale_line_warn', 'varchar')
    util.create_column(cr, "product_template", 'sale_line_warn_msg', 'text')
    util.create_column(cr, "product_template", 'purchase_line_warn', 'varchar')
    util.create_column(cr, "product_template", 'purchase_line_warn_msg', 'text')

    cr.execute(r"""UPDATE product_template t
                      SET sale_line_warn = CASE WHEN s_warn::text[] @> ARRAY['block']
                                                THEN 'block'
                                                WHEN s_warn::text[] @> ARRAY['warning']
                                                THEN 'warning'
                                                ELSE 'no-message'
                                            END,
                          sale_line_warn_msg = array_to_string(s_msg, '\n\n'),
                          purchase_line_warn = CASE WHEN p_warn::text[] @> ARRAY['block']
                                                    THEN 'block'
                                                    WHEN p_warn::text[] @> ARRAY['warning']
                                                    THEN 'warning'
                                                    ELSE 'no-message'
                                                END,
                          purchase_line_warn_msg = array_to_string(p_msg, '\n\n')

                     FROM (SELECT product_tmpl_id,
                                  array_agg(coalesce(sale_line_warn, 'no-message')) s_warn,
                                  {usm} s_msg,
                                  array_agg(coalesce(purchase_line_warn, 'no-message')) p_warn,
                                  {upm} p_msg
                             FROM product_product
                         GROUP BY product_tmpl_id
                     ) AS f
                    WHERE f.product_tmpl_id = t.id
                """.format(usm=util.pg_array_uniq("array_agg(sale_line_warn_msg)", drop_null=True),
                           upm=util.pg_array_uniq("array_agg(purchase_line_warn_msg)", drop_null=True),
                           ))

    cr.execute("""UPDATE product_template
                     SET sale_line_warn = coalesce(sale_line_warn, 'no-message'),
                         purchase_line_warn = coalesce(purchase_line_warn, 'no-message')
               """)

    util.remove_field(cr, 'product.product', 'sale_line_warn')
    util.remove_field(cr, 'product.product', 'sale_line_warn_msg')
    util.remove_field(cr, 'product.product', 'purchase_line_warn')
    util.remove_field(cr, 'product.product', 'purchase_line_warn_msg')
