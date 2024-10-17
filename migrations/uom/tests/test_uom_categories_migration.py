from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.1")
class TestUomCategoriesMigration(UpgradeCase):
    def prepare(self):
        dummy_category = self.env["uom.category"].create(
            {
                "name": "Test Pressure",
            }
        )
        test_uoms = self.env["uom.uom"].create(
            [
                {
                    "name": "Test Pascal",
                    "category_id": dummy_category.id,
                    "uom_type": "reference",
                    "factor_inv": 1.0,
                },
                {
                    "name": "Test Bar",
                    "category_id": dummy_category.id,
                    "uom_type": "bigger",
                    "factor_inv": 100000.0,
                },
                {
                    "name": "Test Atmosphere",
                    "category_id": dummy_category.id,
                    "uom_type": "bigger",
                    "factor_inv": 101325.0,
                },
                {
                    "name": "Test Torr",
                    "category_id": dummy_category.id,
                    "uom_type": "bigger",
                    "factor_inv": 133.322,
                },
                {
                    "name": "Test Barye",
                    "category_id": dummy_category.id,
                    "uom_type": "smaller",
                    "factor_inv": 0.1,
                },
            ]
        )
        return test_uoms.ids

    def check(self, init):
        test_uom_ids = init
        test_uoms = self.env["uom.uom"].browse(test_uom_ids)
        test_pascal = test_uoms.filtered(lambda u: u.name == "Test Pascal")
        self.assertFalse(test_pascal.relative_uom_id, "The reference unit should not have a relative unit")
        self.assertEqual(test_pascal.relative_factor, 1.0, "The reference unit should have a factor of 1.0")
        other_uoms = test_uoms - test_pascal
        self.assertEqual(
            other_uoms.relative_uom_id, test_pascal, "The other units should have the reference unit as relative"
        )
        self.assertEqual(
            other_uoms.mapped("relative_factor"),
            [100000.0, 101325.0, 133.322, 0.1],
            "The other units should have the correct relative factor",
        )
