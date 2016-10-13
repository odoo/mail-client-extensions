# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_pricelist', 'website_id', 'int4')
    util.create_column(cr, 'product_pricelist', 'selectable', 'boolean')

    cr.execute("""
      WITH upd AS (
            UPDATE product_pricelist pl
               SET website_id = w.website_id,
                   selectable = w.selectable
              FROM website_pricelist w
             WHERE w.pricelist_id = pl.id
         RETURNING w.id, w.pricelist_id
      )
      INSERT INTO res_country_group_pricelist_rel(res_country_group_id, pricelist_id)
        SELECT r.res_country_group_id, u.pricelist_id
          FROM res_country_group_website_pricelist_rel r
          JOIN upd u ON (u.id = r.website_pricelist_id)
    """)

    util.delete_model(cr, 'website_pricelist')
    util.remove_field(cr, 'res.country.group', 'website_pricelist_ids')
    cr.execute("DROP TABLE IF EXISTS res_country_group_website_pricelist_rel")
