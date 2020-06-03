# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "product_price_history"):
        # Looks like the module `product_price_history` from OCA is installed
        util.move_model(cr, "product.price.history", "product_price_history", "product")
        util.rename_field(cr, "product.price.history", "product_id", "product_template_id")  # FK is correct
        util.rename_field(cr, "product.price.history", "amount", "cost")
        util.uninstall_module(cr, "product_price_history")
        return

    # NOTE: the orm will create FK
    cr.execute("""CREATE TABLE product_price_history(
                    id SERIAL NOT NULL,
                    company_id integer,
                    product_template_id integer,
                    datetime timestamp without time zone,
                    cost float8,
                    PRIMARY KEY(id)
                  )
               """)

    main_company = util.ref(cr, 'base.main_company')
    cr.execute("""
        INSERT INTO product_price_history(cost, product_template_id, company_id, datetime)
        SELECT standard_price, id, COALESCE(company_id, %s, (SELECT MIN(id) FROM res_company)),
               NOW() AT TIME ZONE 'UTC'
          FROM product_template
    """, (main_company,))
