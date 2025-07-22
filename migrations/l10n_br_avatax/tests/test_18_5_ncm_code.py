from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("18.5")
class CheckNCMCode(UpgradeCase):
    def prepare(self):
        empty_ncm = self.env["l10n_br.ncm.code"].create({})
        test_ncm = self.env.ref("l10n_br_avatax.30069110")

        # Copy twice to test three ncm codes with the same name/code combination.
        duplicate_ncm_code = test_ncm.copy().copy()

        # Make sure we prefer keeping NCM records with an XML ID. To simulate the user
        # having deleted and reloaded the codes, assign the xml id to the duplicated
        # NCM code.
        xml_id = self.env["ir.model.data"].search(
            [("module", "=", "l10n_br_avatax"), ("name", "=", "30069110")], limit=1
        )
        xml_id.res_id = duplicate_ncm_code.id

        product = self.env["product.template"].create({"name": "test product", "l10n_br_ncm_code_id": test_ncm.id})

        return {
            "empty_ncm_id": empty_ncm.id,
            "duplicated_ncm_id": duplicate_ncm_code.id,
            "product_id": product.id,
        }

    def check(self, init):
        NCMCode = self.env["l10n_br.ncm.code"]
        empty_ncm = NCMCode.browse(init["empty_ncm_id"])
        self.assertRecordValues(
            empty_ncm, [{"code": str(empty_ncm.id), "name": str(empty_ncm.id)}]
        )  # code and name should have received default values

        ncm = NCMCode.browse(init["duplicated_ncm_id"])
        self.assertEqual(
            ncm,
            self.env.ref("l10n_br_avatax.30069110"),
            "Should have kept the NCM with XML ID.",
        )

        self.assertTrue(
            ncm.name.startswith("Produtos farmacêuticos"),
            "The 3006.91.10 code should have been removed from the name.",
        )

        self.assertEqual(
            self.env["l10n_br.ncm.code"].search_count(
                [
                    ("name", "=", ncm.name),
                    ("code", "=", ncm.code),
                ]
            ),
            1,
            "Only one NCM code should remain.",
        )

        self.assertEqual(
            self.env["product.template"].browse(init["product_id"]).l10n_br_ncm_code_id,
            ncm,
            "The product should have been assigned the original NCM code when the duplicate codes were deleted.",
        )
