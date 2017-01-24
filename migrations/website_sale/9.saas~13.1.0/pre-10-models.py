# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_pricelist', 'website_id', 'int4')
    util.create_column(cr, 'product_pricelist', 'selectable', 'boolean')

    # A default website_pricelist is created by module data. Users may not realise it, but it
    # restrict main pricelist to europe by default (only on ecommerce < saas-13).
    # This is not necessary what users want in backend. Only keep it if modified by user (as the
    # record is in noupdate, only user can modify the write date).
    wlist0 = util.ref(cr, 'website_sale.wlist0')
    europe = util.ref(cr, 'base.europe')
    if wlist0 and europe:
        cr.execute("""
            DELETE FROM res_country_group_website_pricelist_rel r
                  USING website_pricelist p
                  WHERE r.res_country_group_id = %s
                    AND r.website_pricelist_id = p.id
                    AND p.id = %s
                    AND p.create_date = p.write_date
        """, [europe, wlist0])

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
