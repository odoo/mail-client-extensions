# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move_line", "intrastat_product_origin_country_id", 'int4')

    cr.execute("""
        UPDATE account_move_line aml
           SET intrastat_product_origin_country_id=t.intrastat_origin_country_id
          FROM product_product p
    INNER JOIN product_template t on p.product_tmpl_id=t.id
         WHERE p.id=aml.product_id
    """)
