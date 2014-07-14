# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, "product_template", "available_in_pos", "boolean")
    util.create_column(cr, "product_template", "income_pdt", "boolean")
    util.create_column(cr, "product_template", "expense_pdt", "boolean")
    util.create_column(cr, "product_template", "to_weight", "boolean")

    cr.execute("""UPDATE product_template
                     SET available_in_pos='t',
                         income_pdt='f',
                         expense_pdt='f',
                         to_weight='f'
               """)

    cr.execute("""UPDATE product_template t
                     SET available_in_pos = p.in_pos,
                         income_pdt = p.inc,
                         expense_pdt = p.exp,
                         to_weight = p.tow
                    FROM (SELECT product_tmpl_id,
                                 MAX(p.available_in_pos::int)::boolean as in_pos,
                                 MAX(p.income_pdt::int)::boolean as inc,
                                 MAX(p.expense_pdt::int)::boolean as exp,
                                 MAX(p.to_weight::int)::boolean as tow
                            FROM product_product p
                        GROUP BY product_tmpl_id
                    ) AS p
                   WHERE t.id = p.product_tmpl_id
               """)

    util.remove_field(cr, "product.product", "available_in_pos")
    util.remove_field(cr, "product.product", "income_pdt")
    util.remove_field(cr, "product.product", "expense_pdt")
    util.remove_field(cr, "product.product", "to_weight")
