# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):

    cr.execute("UPDATE stock_move SET priority = '2' WHERE priority = '1'")

    # Verify incompatible UoM on stock.move vs product UoM and warn about it
    cr.execute(
        """
        SELECT count(*) FROM stock_move m
            JOIN product_product p ON (m.product_id = p.id)
            JOIN product_template t ON (t.id=p.product_tmpl_id)
            JOIN product_uom u1 ON (u1.id = m.product_uom)
            JOIN product_uom u2 ON (u2.id = t.uom_id)
        WHERE u1.category_id != u2.category_id;
    """
    )
    count = cr.fetchone()[0]
    if count:
        header = """
        <p>Warning when upgrading Odoo to version {version}.</p>
        <h2>Stock moves with incompatible unit of measure</h2>
        """

        footer = ""

        msg = (
            "Found %s stock.move entries with a Units of Measure "
            "incompatible with the default product UoM (different "
            "categories). We have forced them to the default product "
            "UoM"
            ""
        ) % count
        util.announce(cr, "8.0", msg, recipient=None, header=header, footer=footer)
        cr.execute(
            """
            UPDATE stock_move m SET product_uom = t.uom_id
                FROM product_product p, product_template t, product_uom u1, product_uom u2
                WHERE (m.product_id = p.id) AND (t.id=p.product_tmpl_id) AND (u1.id = m.product_uom) AND
                      (u2.id = t.uom_id) AND u1.category_id != u2.category_id;
        """
        )
