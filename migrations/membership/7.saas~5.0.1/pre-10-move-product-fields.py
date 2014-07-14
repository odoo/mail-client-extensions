# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, "product_template", "membership", "boolean")
    util.create_column(cr, "product_template", "membership_date_from", "date")
    util.create_column(cr, "product_template", "membership_date_to", "date")

    cr.execute("UPDATE product_template SET membership='f'")

    cr.execute("""UPDATE product_template t
                     SET membership = p.membership,
                         membership_date_from = p.date_from,
                         membership_date_to = p.date_to
                    FROM (SELECT product_tmpl_id,
                                 MAX(p.membership::int)::boolean as membership,
                                 MIN(p.membership_date_from) as date_from,
                                 MAX(p.membership_date_to) as date_to
                            FROM product_product p
                        GROUP BY product_tmpl_id
                    ) AS p
                   WHERE t.id = p.product_tmpl_id
               """)

    util.remove_field(cr, "product.product", "membership")
    util.remove_field(cr, "product.product", "membership_date_from")
    util.remove_field(cr, "product.product", "membership_date_to")
