import unittest

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import IntegrityCase


@unittest.skipIf(util.version_gte("saas~18.1"), "UoM categories are removed in 18.1")
class TestUoMConsistencyChanges(IntegrityCase):
    def check(self, value):
        new = set(self.invariant()) - set(value)

        self.assertFalse(
            new,
            "New stock move lines UoM inconsistencies introduced during the migration",
        )

    def invariant(self):
        cr = self.env.cr
        cr.execute(
            """
              SELECT sml.id
                FROM stock_move_line sml
                JOIN product_product pp ON pp.id = sml.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                JOIN uom_uom uom1 ON uom1.id = sml.product_uom_id
                JOIN uom_uom uom2 ON uom2.id = pt.uom_id
               WHERE uom1.category_id != uom2.category_id
            """
        )
        return [r[0] for r in cr.fetchall()]
