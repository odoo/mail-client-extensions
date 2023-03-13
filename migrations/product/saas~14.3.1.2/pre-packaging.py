# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "delivery"):
        for table, _column, constraint, _action in util.get_fk(cr, "product_packaging"):
            cr.execute(f"ALTER TABLE {table} DROP CONSTRAINT {constraint}")

        util.rename_model(cr, "product.packaging", "stock.package.type")
        # This model is actually defined in the `stock` module (hence the name). It works because `delivery` depends on `stock`.
        util.move_model(
            cr,
            "stock.package.type",
            "product",
            "stock",
            keep={"product_packaging_form_view2", "product_packaging_tree_view2"},
        )

        cr.execute(
            """
                CREATE TABLE product_packaging AS
                  SELECT id,
                         create_uid,
                         create_date,
                         write_uid,
                         write_date,
                         name,
                         sequence,
                         product_id,
                         qty,
                         barcode,
                         company_id
                    FROM stock_package_type
                   WHERE product_id IS NOT NULL
            """
        )
        cr.execute("ALTER TABLE product_packaging ADD PRIMARY KEY (id)")
        cr.execute("ALTER TABLE product_packaging ALTER COLUMN id SET NOT NULL")
        cr.execute(
            """
            CREATE SEQUENCE product_packaging_id_seq OWNED BY product_packaging.id;
            SELECT Setval('product_packaging_id_seq', COALESCE(Max(id), 0) + 1, false)
              FROM product_packaging;
            ALTER TABLE product_packaging
              ALTER COLUMN id SET DEFAULT NEXTVAL('product_packaging_id_seq'::regclass);
        """
        )
        cr.execute("DELETE FROM stock_package_type WHERE product_id IS NOT NULL")
        util.remove_field(cr, "stock.package.type", "qty")
        util.remove_field(cr, "stock.package.type", "product_id")
        util.remove_field(cr, "stock.package.type", "product_uom_id")
