import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("17.2")
class TestBrokenRevisionHistoryWithNoSnapshot(UpgradeCase):
    def prepare(self):
        self.skipTest("We do not have solution for this test yet")
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

        # Case 1: With gaps with no snapshot.
        #
        # Revision history:
        #                head A
        #                     |
        #                     B
        #                     |
        #                     C
        #                    / X
        #                   /   X
        #                  F     D
        #                  |     |
        #                  G     E
        #                 X \
        #                X   \
        #               H     J
        #               |
        #               I

        case_1_revision_ids = []
        case_1_a = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "A",
                    "parent_revision_id": False if util.version_gte("saas~17.2") else "START_REVISION",
                },
            ]
        )
        case_1_revision_ids.append(case_1_a.id)

        case_1_b = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "B",
                    "parent_revision_id": case_1_a.id if util.version_gte("saas~17.2") else "A",
                },
            ]
        )
        case_1_revision_ids.append(case_1_b.id)

        case_1_c = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "C",
                    "parent_revision_id": case_1_b.id if util.version_gte("saas~17.2") else "B",
                },
            ]
        )
        case_1_revision_ids.append(case_1_c.id)

        case_1_d = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "D",
                    "parent_revision_id": case_1_c.id if util.version_gte("saas~17.2") else "C",
                },
            ]
        )
        case_1_revision_ids.append(case_1_d.id)

        case_1_e = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "E",
                    "parent_revision_id": case_1_d.id if util.version_gte("saas~17.2") else "D",
                },
            ]
        )
        case_1_revision_ids.append(case_1_e.id)

        # DELETE the revision D and continue adding on top of C
        self.env.cr.execute("DELETE FROM spreadsheet_revision WHERE id = %s", [case_1_d.id])

        case_1_f = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "F",
                    "parent_revision_id": case_1_c.id if util.version_gte("saas~17.2") else "C",
                },
            ]
        )
        case_1_revision_ids.append(case_1_f.id)

        case_1_g = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "G",
                    "parent_revision_id": case_1_f.id if util.version_gte("saas~17.2") else "F",
                },
            ]
        )
        case_1_revision_ids.append(case_1_g.id)

        case_1_h = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "H",
                    "parent_revision_id": case_1_g.id if util.version_gte("saas~17.2") else "G",
                },
            ]
        )
        case_1_revision_ids.append(case_1_h.id)

        case_1_i = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "I",
                    "parent_revision_id": case_1_h.id if util.version_gte("saas~17.2") else "H",
                },
            ]
        )
        case_1_revision_ids.append(case_1_i.id)

        # DELETE the revision H and continue adding on top of G
        self.env.cr.execute("DELETE FROM spreadsheet_revision WHERE id = %s", [case_1_h.id])

        case_1_j = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000001,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "J",
                    "parent_revision_id": case_1_g.id if util.version_gte("saas~17.2") else "G",
                },
            ]
        )
        case_1_revision_ids.append(case_1_j.id)

        # Case 2: There is gap after deleting last snapshot
        #
        # Revision history:
        #                head A
        #                     |
        #                     B
        #                     |
        #                     C
        #                     |
        #                     D
        #                     |
        #                     E
        #                      X
        #                       X
        #                        F snapshot
        #                        |
        #                        G
        #                        |
        #                        H

        case_2_revision_ids = []
        case_2_a = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000002,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "A",
                    "parent_revision_id": False if util.version_gte("saas~17.2") else "START_REVISION",
                },
            ]
        )
        case_2_revision_ids.append(case_2_a.id)

        case_2_b = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000002,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "B",
                    "parent_revision_id": case_2_a.id if util.version_gte("saas~17.2") else "A",
                },
            ]
        )
        case_2_revision_ids.append(case_2_b.id)

        case_2_c = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000002,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "C",
                    "parent_revision_id": case_2_b.id if util.version_gte("saas~17.2") else "B",
                },
            ]
        )
        case_2_revision_ids.append(case_2_c.id)

        case_2_d = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000002,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "D",
                    "parent_revision_id": case_2_c.id if util.version_gte("saas~17.2") else "C",
                },
            ]
        )
        case_2_revision_ids.append(case_2_d.id)

        case_2_e = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000002,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "E",
                    "parent_revision_id": case_2_d.id if util.version_gte("saas~17.2") else "D",
                },
            ]
        )
        case_2_revision_ids.append(case_2_e.id)

        case_2_f = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000002,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(snapshot_command),
                    field_name: "F",
                    "parent_revision_id": case_2_e.id if util.version_gte("saas~17.2") else "E",
                },
            ]
        )
        case_2_revision_ids.append(case_2_f.id)

        case_2_g = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000002,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "G",
                    "parent_revision_id": case_2_f.id if util.version_gte("saas~17.2") else "F",
                },
            ]
        )
        case_2_revision_ids.append(case_2_g.id)

        case_2_h = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2000002,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_command),
                    field_name: "H",
                    "parent_revision_id": case_2_g.id if util.version_gte("saas~17.2") else "G",
                },
            ]
        )
        case_2_revision_ids.append(case_2_h.id)

        return [case_1_revision_ids, case_2_revision_ids]

    def check(self, upgrade_cases):
        self.assertEqual(1, 1)
