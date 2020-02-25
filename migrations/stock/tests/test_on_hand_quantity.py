# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.base.maintenance.migrations.testing import IntegrityCase


class TestOnHandQuantityUnchanged(IntegrityCase):
    def invariant(self):
        self.env.cr.execute(
            """ SELECT pp.id
                FROM product_product pp
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                AND pp.active = TRUE AND pt.TYPE = 'product'
                ORDER BY pp.id
            """
        )
        products = self.env["product.product"].browse([row[0] for row in self.env.cr.fetchall()])
        return products.mapped(lambda p: [p.id, p.qty_available])
