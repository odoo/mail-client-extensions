from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestCzTaxTags(UpgradeCase):
    def prepare(self):
        company = self.env["res.company"].create({"name": "company no tax_tag_invert CZ"})
        ACT = self.env["account.chart.template"].with_company(company)
        ACT.try_loading("cz", company)
        move = self.env["account.move"].create({
            "move_type": "in_invoice",
            "journal_id": ACT.ref("purchase").id,
            "line_ids": [
                (0, 0, {
                    "name": "l10n_cz_12_purchase_goods_eu",
                    "price_unit": 100,
                    "tax_ids": [(6, 0, ACT.ref("l10n_cz_12_purchase_goods_eu").ids)],
                }),
            ]
        })
        self.assertEqual(
            move.line_ids.mapped(lambda line: (line.balance, line.tax_tag_ids.mapped("name"))),
            [
                (100.0, ["+VAT 4 Base"]),
                (12.0, []),
                (-12.0, ["-VAT 4 Tax"]),
                (-100.0, []),
            ],
        )
        return {
            "move_id": move.id,
            "company_id": company.id,
        }

    def check(self, data):
        move = self.env["account.move"].browse(data["move_id"])
        self.assertEqual(
            move.line_ids.mapped(lambda line: (line.balance, line.tax_tag_ids.mapped("name"))),
            [
                (100.0, ["VAT 4 Base"]),
                (12.0, ["VAT 4 Tax"]),
                (-12.0, []),
                (-100.0, []),
            ],
        )
        correction_lines = self.env["account.move.line"].search([
            ("journal_id.code", "=", "UPGTAG"),
            ("company_id", "=", data["company_id"]),
        ])
        self.assertEqual(
            correction_lines.mapped(lambda line: (line.balance, line.tax_tag_ids.mapped("name"))),
            [],
        )
