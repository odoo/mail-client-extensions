import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("17.2")
class TestBrokenRevisionHistory(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None

        revision_command = {
            "type": "REMOTE_REVISION",
            "commands": [],
        }

        snapshot_command = {
            "type": "SNAPSHOT_CREATED",
            "commands": [],
        }

        field_name = "revision_uuid" if util.version_gte("saas~17.2") else "revision_id"

        # Case 1: No gap and No snapshot
        #
        # Revision history before upgrade:
        #                     A head
        #                     |
        #                     B
        #                     |
        #                     C
        #                     |
        #                     D
        #

        no_gap_no_snapshot = []
        case_1_a = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000000,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "A",
                    "parent_revision_id": False if util.version_gte("saas~17.2") else "START_REVISION",
                },
            ]
        )
        no_gap_no_snapshot.append(case_1_a.id)

        case_1_b = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000000,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "B",
                    "parent_revision_id": case_1_a.id if util.version_gte("saas~17.2") else "A",
                },
            ]
        )
        no_gap_no_snapshot.append(case_1_b.id)

        case_1_c = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000000,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "C",
                    "parent_revision_id": case_1_b.id if util.version_gte("saas~17.2") else "B",
                },
            ]
        )
        no_gap_no_snapshot.append(case_1_c.id)

        case_1_d = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000000,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "D",
                    "parent_revision_id": case_1_c.id if util.version_gte("saas~17.2") else "C",
                },
            ]
        )
        no_gap_no_snapshot.append(case_1_d.id)

        # Case 2: No gap with snapshots
        #
        # Revision history before upgrade:
        #                     A head
        #                     |
        #                     B
        #                     |
        #                     C snapshot
        #                     |
        #                     D
        #                     |
        #                     E snapshot
        #                     |
        #                     F
        #

        no_gap_with_snapshots = []
        case_2_a = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "A",
                    "parent_revision_id": False if util.version_gte("saas~17.2") else "START_REVISION",
                },
            ]
        )
        no_gap_with_snapshots.append(case_2_a.id)

        case_2_b = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "B",
                    "parent_revision_id": case_2_a.id if util.version_gte("saas~17.2") else "A",
                },
            ]
        )
        no_gap_with_snapshots.append(case_2_b.id)

        case_2_c = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(snapshot_command),
                    field_name: "C",
                    "parent_revision_id": case_2_b.id if util.version_gte("saas~17.2") else "B",
                },
            ]
        )
        no_gap_with_snapshots.append(case_2_c.id)

        case_2_d = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "D",
                    "parent_revision_id": case_2_c.id if util.version_gte("saas~17.2") else "C",
                },
            ]
        )
        no_gap_with_snapshots.append(case_2_d.id)

        case_2_e = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(snapshot_command),
                    field_name: "E",
                    "parent_revision_id": case_2_d.id if util.version_gte("saas~17.2") else "D",
                },
            ]
        )
        no_gap_with_snapshots.append(case_2_e.id)

        case_2_f = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "F",
                    "parent_revision_id": case_2_e.id if util.version_gte("saas~17.2") else "E",
                },
            ]
        )
        no_gap_with_snapshots.append(case_2_f.id)

        # Case 3: With gap and with snapshots
        #
        # Revision history before upgrade:
        #                head A
        #                     |
        #                     B
        #                     |
        #                     C snapshot
        #                    / X
        #                   /   X
        #                  G     D
        #                  |     |
        #         snapshot H     E
        #                  |     |
        #                  I     F
        #                  |
        #                  J
        #                 X \
        #                X   \
        #               K     M
        #               |
        #               L

        with_gap_with_snapshots = []
        case_3_a = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "A",
                    "parent_revision_id": False if util.version_gte("saas~17.2") else "START_REVISION",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_a.id)

        case_3_b = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "B",
                    "parent_revision_id": case_3_a.id if util.version_gte("saas~17.2") else "A",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_b.id)

        case_3_c = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(snapshot_command),
                    field_name: "C",
                    "parent_revision_id": case_3_b.id if util.version_gte("saas~17.2") else "B",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_c.id)

        case_3_d = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "D",
                    "parent_revision_id": case_3_c.id if util.version_gte("saas~17.2") else "C",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_d.id)

        case_3_e = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "E",
                    "parent_revision_id": case_3_d.id if util.version_gte("saas~17.2") else "D",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_e.id)

        case_3_f = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "F",
                    "parent_revision_id": case_3_e.id if util.version_gte("saas~17.2") else "E",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_f.id)

        # DELETE the revision D and continue adding on top of C
        self.env.cr.execute("DELETE FROM spreadsheet_revision WHERE id = %s", [case_3_d.id])

        case_3_g = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "G",
                    "parent_revision_id": case_3_c.id if util.version_gte("saas~17.2") else "C",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_g.id)

        case_3_h = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(snapshot_command),
                    field_name: "H",
                    "parent_revision_id": case_3_g.id if util.version_gte("saas~17.2") else "G",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_h.id)

        case_3_i = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "I",
                    "parent_revision_id": case_3_h.id if util.version_gte("saas~17.2") else "H",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_i.id)

        case_3_j = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "J",
                    "parent_revision_id": case_3_i.id if util.version_gte("saas~17.2") else "I",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_j.id)

        case_3_k = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "K",
                    "parent_revision_id": case_3_j.id if util.version_gte("saas~17.2") else "J",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_k.id)

        case_3_l = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "L",
                    "parent_revision_id": case_3_k.id if util.version_gte("saas~17.2") else "K",
                },
            ]
        )
        with_gap_with_snapshots.append(case_3_l.id)

        # DELETE the revision K and continue adding on top of J
        self.env.cr.execute("DELETE FROM spreadsheet_revision WHERE id = %s", [case_3_k.id])

        case_3_m = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000003,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "M",
                    "parent_revision_id": case_3_j.id if util.version_gte("saas~17.2") else "J",
                },
            ]
        )

        with_gap_with_snapshots.append(case_3_m.id)

        return [no_gap_no_snapshot, no_gap_with_snapshots, with_gap_with_snapshots]

    def check(self, upgrade_cases):
        if not upgrade_cases:
            return
        if len(upgrade_cases[0]) > 0:
            self.assertEqual(len(upgrade_cases[0]), 4)
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[0][0]).exists())
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[0][1]).exists())
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[0][2]).exists())
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[0][3]).exists())

        if len(upgrade_cases[1]) > 0:
            self.assertEqual(len(upgrade_cases[1]), 6)
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[1][0]).exists())
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[1][1]).exists())
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[1][2]).exists())
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[1][3]).exists())
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[1][4]).exists())
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[1][5]).exists())

        if len(upgrade_cases[2]) > 0:
            self.assertEqual(len(upgrade_cases[2]), 13)
            self.assertFalse(self.env["spreadsheet.revision"].browse(upgrade_cases[2][0]).exists())
            self.assertFalse(self.env["spreadsheet.revision"].browse(upgrade_cases[2][1]).exists())
            self.assertFalse(self.env["spreadsheet.revision"].browse(upgrade_cases[2][2]).exists())
            self.assertFalse(self.env["spreadsheet.revision"].browse(upgrade_cases[2][3]).exists())
            self.assertFalse(self.env["spreadsheet.revision"].browse(upgrade_cases[2][4]).exists())
            self.assertFalse(self.env["spreadsheet.revision"].browse(upgrade_cases[2][5]).exists())
            self.assertFalse(self.env["spreadsheet.revision"].browse(upgrade_cases[2][6]).exists())

            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[2][7]).exists())
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[2][8]).exists())
            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[2][9]).exists())

            self.assertFalse(self.env["spreadsheet.revision"].browse(upgrade_cases[2][10]).exists())
            self.assertFalse(self.env["spreadsheet.revision"].browse(upgrade_cases[2][11]).exists())

            self.assertTrue(self.env["spreadsheet.revision"].browse(upgrade_cases[2][12]).exists())
