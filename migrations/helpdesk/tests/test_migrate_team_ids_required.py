# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.3")
class TestMigrateTeamIdsRequired(UpgradeCase):
    def prepare(self):
        # Create stages without any teams linked
        stage1, stage2, stage3, stage4 = self.env["helpdesk.stage"].create(
            [
                {"name": "Unused stage"},
                {"name": "Stage with 1 ticket"},
                {"name": "Stage with 2 tickets"},
                {"name": "Stage with 1 SLA"},
            ]
        )

        # Create 2 helpdesk team to linked the tickets
        team1, team2 = self.env["helpdesk.team"].create(
            [
                {"name": "Test Team 1"},
                {"name": "Test Team 2"},
            ]
        )

        self.env["helpdesk.ticket"].create(
            [
                {"name": "ticket 1", "team_id": team1.id, "stage_id": stage2.id},
                {"name": "ticket 1", "team_id": team1.id, "stage_id": stage3.id},
                {"name": "ticket 1", "team_id": team2.id, "stage_id": stage3.id},
            ]
        )

        self.env["helpdesk.sla"].create(
            {
                "name": "SLA",
                "team_id": team1.id,
                "time": 32,
                "stage_id": stage4.id,
                "priority": "1",
            }
        )

        return stage1.id, stage2.id, stage3.id, stage4.id, team1.id, team2.id

    def check(self, init):
        stage1_id, stage2_id, stage3_id, stage4_id, team1_id, team2_id = init
        stages = self.env["helpdesk.stage"].search(
            [
                ("id", "in", [stage1_id, stage2_id, stage3_id, stage4_id]),
            ],
            order="id",
        )
        teams = self.env["helpdesk.team"].browse([team1_id, team2_id])

        self.assertEqual(len(stages), 3)
        self.assertIn(stage2_id, stages.ids)
        self.assertIn(stage3_id, stages.ids)
        self.assertIn(stage4_id, stages.ids)
        teams_in_stage2 = stages.filtered(lambda s: s.id == stage2_id).team_ids
        self.assertEqual(len(teams_in_stage2), 1)
        self.assertEqual(teams_in_stage2.id, team1_id)
        teams_in_stage3 = stages.filtered(lambda s: s.id == stage3_id).team_ids
        self.assertEqual(len(teams_in_stage3), 2)
        self.assertEqual(teams_in_stage3, teams)
        teams_in_stage4 = stages.filtered(lambda s: s.id == stage4_id).team_ids
        self.assertEqual(len(teams_in_stage4), 1)
        self.assertEqual(teams_in_stage4.id, team1_id)
