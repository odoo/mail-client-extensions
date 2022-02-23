# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Two packagings can not have the same barcode
    cr.execute(
        """
        SELECT pack01.id, pack01.name, pack01.barcode, tmpl.name
        FROM product_packaging pack01
        LEFT JOIN product_product prod on pack01.product_id = prod.id
        LEFT JOIN product_template tmpl on prod.product_tmpl_id = tmpl.id
        WHERE pack01.barcode != ''
        AND EXISTS (SELECT pack02.id
                    FROM product_packaging pack02
                    WHERE pack01.id != pack02.id and pack01.barcode = pack02.barcode)
        ORDER BY pack01.barcode, pack01.name
        """
    )
    duplicates = []
    ids = []
    for id, pack_name, barcode, prod_name in cr.fetchall():
        duplicates.append("%s: %s (%s)" % (barcode, pack_name, prod_name))
        ids.append(id)
    if duplicates:
        duplicates = "\n".join(duplicates)
        msg = (
            "Some packagings have the same barcode. This is not possible in the new version.\n"
            "The duplicated barcodes have been removed. Here is the list:\n"
            "(barcode: packaging name (product name))\n"
            "%s" % duplicates
        )
        cr.execute(
            """
            UPDATE product_packaging
            SET barcode = null
            WHERE id in %s
            """,
            [tuple(ids)],
        )
        util.add_to_migration_reports(msg, "Products & Pricelists")

    # A product and a packaging can not have the same barcode
    cr.execute(
        """
        SELECT pack.id, pack.barcode, prod_tmpl.name, pack.name, pack_tmpl.name
        FROM product_product prod
        INNER JOIN product_packaging pack ON prod.barcode = pack.barcode
        LEFT JOIN product_product pack_prod on pack.product_id = pack_prod.id
        LEFT JOIN product_template pack_tmpl on pack_prod.product_tmpl_id = pack_tmpl.id
        LEFT JOIN product_template prod_tmpl on prod.product_tmpl_id = prod_tmpl.id
        WHERE prod.barcode != ''
        """
    )
    duplicates = []
    ids = []
    for id, barcode, prod_name, pack_name, pack_prod_name in cr.fetchall():
        duplicates.append("%s: %s -- %s (%s)" % (barcode, prod_name, pack_name, pack_prod_name))
        ids.append(id)
    if duplicates:
        duplicates = "\n".join(duplicates)
        msg = (
            "Some products and packagings share the same barcode. This is not possible in the new version.\n"
            "The barcodes of these packagings have been removed. Here is the list of all conflicts:\n"
            "(barcode: product name -- package name (name of the product related to the package))\n"
            "%s" % duplicates
        )
        cr.execute(
            """
            UPDATE product_packaging
            SET barcode = null
            WHERE id in %s
            """,
            [tuple(ids)],
        )
        util.add_to_migration_reports(msg, "Products & Pricelists")

    util.remove_field(cr, "res.config.settings", "module_sale_product_configurator")
