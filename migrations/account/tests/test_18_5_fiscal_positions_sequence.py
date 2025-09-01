from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestFiscalPositionsSequence(UpgradeCase):
    def prepare(self):
        company_1 = self.env["res.company"].create({"name": "company 1"})
        company_2 = self.env["res.company"].create({"name": "company 2"})
        country = self.env["res.country"].create({"name": "country", "code": "AA"})
        state_1, state_2, state_3 = self.env["res.country.state"].create(
            [{"name": f"state{i}", "country_id": country.id, "code": f"A{'ABC'[i]}"} for i in range(3)]
        )
        positions = self.env["account.fiscal.position"].create(
            [
                {
                    "name": "co 1 fpos 1",
                    "company_id": company_1.id,
                    "auto_apply": True,
                    "vat_required": False,
                    "sequence": 1,
                },
                {
                    "name": "co 1 fpos 2",
                    "company_id": company_1.id,
                    "auto_apply": False,
                    "vat_required": True,
                    "sequence": 2,
                },
                {
                    "name": "co 1 fpos 3",
                    "company_id": company_1.id,
                    "auto_apply": True,
                    "vat_required": True,
                    "sequence": 3,
                },
                {
                    "name": "co 1 fpos 4",
                    "company_id": company_1.id,
                    "auto_apply": True,
                    "state_ids": state_1.ids,
                    "sequence": 4,
                },
                {
                    "name": "co 1 fpos 5",
                    "company_id": company_1.id,
                    "auto_apply": True,
                    "state_ids": state_2.ids,
                    "sequence": 5,
                },
                {
                    "name": "co 1 fpos 6",
                    "company_id": company_1.id,
                    "auto_apply": True,
                    "state_ids": state_3.ids,
                    "sequence": 6,
                },
                {
                    "name": "co 2 fpos 1",
                    "company_id": company_2.id,
                    "auto_apply": True,
                },
                {
                    "name": "co 1 fpos 7",
                    "company_id": company_1.id,
                    "auto_apply": True,
                    "zip_from": "1000",
                    "zip_to": "2000",
                    "sequence": 7,
                },
                {
                    "name": "co 2 fpos 2",
                    "company_id": company_2.id,
                    "auto_apply": True,
                    "sequence": 20,
                },
                {
                    "name": "co 2 fpos 3",
                    "company_id": company_2.id,
                    "auto_apply": True,
                    "sequence": 30,
                },
                {
                    "name": "co 2 fpos 4",
                    "company_id": company_2.id,
                    "auto_apply": True,
                    "sequence": 40,
                    "vat_required": True,
                },
            ]
        )

        return positions.ids

    def check(self, init):
        sequences = self.env["account.fiscal.position"].browse(init).mapped("sequence")
        expected = [6, 2, 1, 3, 4, 5, 2, 2, 3, 4, 1]
        self.assertEqual(sequences, expected, "The fiscal positions sequences are not as expected after the upgrade.")
