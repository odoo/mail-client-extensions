from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.2")
class TestICPToDomain(UpgradeCase):
    def prepare(self):
        stages = self.env["crm.stage"].create(
            [
                {
                    "name": "New Stage",
                    "sequence": 1,
                },
                {
                    "is_won": True,
                    "name": "Won Stage",
                    "sequence": 2,
                },
            ]
        )
        leads = self.env["crm.lead"].create(
            [
                {
                    "name": "New",
                    "probability": 50,
                    "stage_id": stages[0].id,
                },
                {
                    "active": True,
                    "name": "Won, bad probability",
                    "probability": 50,
                    "stage_id": stages[1].id,
                },
                {
                    "active": True,
                    "name": "Won ok",
                    "probability": 100,
                    "stage_id": stages[1].id,
                },
                {
                    "active": False,
                    "name": "Lost",
                    "probability": 0,
                    "stage_id": stages[0].id,
                },
                {
                    "active": False,
                    "name": "Archived, not lost",
                    "probability": 50,
                    "stage_id": stages[0].id,
                },
            ]
        )
        return {
            "lead_ids": leads.ids,
        }

    def check(self, init):
        leads = self.env["crm.lead"].browse(init["lead_ids"])
        for lead, (probability, won_status) in zip(
            leads,
            [
                (50, "pending"),
                (100, "won"),  # should update probability
                (100, "won"),
                (0, "lost"),
                (50, "pending"),
            ],
        ):
            with self.subTest(lead_name=lead.name):
                self.assertEqual(lead.probability, probability)
                self.assertEqual(lead.won_status, won_status)
