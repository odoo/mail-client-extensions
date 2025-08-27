from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestBeTaxTags(UpgradeCase):
    def prepare(self):
        company = self.env["res.company"].create({"name": "company no tax_tag_invert BE"})
        ACT = self.env["account.chart.template"].with_company(company)
        ACT.try_loading("be_comp", company)
        move = self.env["account.move"].create({
            "move_type": "in_invoice",
            "journal_id": ACT.ref("purchase").id,
            "line_ids": [
                (0, 0, {
                    "name": "attn_VAT-IN-V82-21-EU-S-D50",
                    "price_unit": 100,
                    "tax_ids": [(6, 0, ACT.ref("attn_VAT-IN-V82-21-EU-S-D50").ids)],
                }),
                (0, 0, {
                    "name": "attn_VAT-IN-V82-21-EU-G-D35-ALRD-IN-BE",
                    "price_unit": 100,
                    "tax_ids": [(6, 0, ACT.ref("attn_VAT-IN-V82-21-EU-G-D35-ALRD-IN-BE").ids)],
                }),
                (0, 0, {
                    "name": "attn_VAT-IN-V82-12-EU-S",
                    "price_unit": 100,
                    "tax_ids": [(6, 0, ACT.ref("attn_VAT-IN-V82-12-EU-S").ids)],
                }),
            ]
        })
        self.assertEqual(
            move.line_ids.mapped(lambda line: (line.balance, line.tax_tag_ids.mapped("name"))),
            [
                (100.0, ["+82", "+88"]),
                (100.0, ["+82", "+87"]),
                (100.0, ["+82", "+88"]),
                (10.5, ["+59"]),
                (10.5, ["+82", "+88"]),
                (-21.0, ["-55"]),
                (13.65, ["+82"]),
                (7.35, ["+59"]),
                (-21.0, ["+56"]),
                (12.0, ["+59"]),
                (-12.0, ["-55"]),
                (-300.0, []),
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
                (100.0, ["82", "88"]),
                (100.0, ["82", "87"]),
                (100.0, ["82", "88"]),
                (10.5, ["59"]),
                (10.5, ["82", "88"]),
                (-21.0, ["55"]),
                (13.65, ["82"]),
                (7.35, ["59"]),
                (-21.0, ["56"]),
                (12.0, ["59"]),
                (-12.0, ["55"]),
                (-300.0, []),
            ],
        )
        correction_lines = self.env["account.move.line"].search([
            ("journal_id.code", "=", "UPGTAG"),
            ("company_id", "=", data["company_id"]),
        ])
        self.assertEqual(
            correction_lines.mapped(lambda line: (line.balance, line.tax_tag_ids.mapped("name"))),
            [
                (42.0, ["56"]),
                (-42.0, [])
            ],
        )
