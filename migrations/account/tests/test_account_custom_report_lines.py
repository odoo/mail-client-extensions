from odoo.addons.base.maintenance.migrations.testing import UpgradeCase
from odoo.addons.base.maintenance.migrations.util import version_gte


class TestResequencedCustomLines(UpgradeCase):
    """
    Test `0.0.0/{pre,end}-20-resequence-custom-report-line.py`
    """

    def prepare(self):
        if not version_gte("16.0"):
            return self.skipTest("This test is meant to run on Odoo 16+")

        ar = self.env["account.report"]
        arl = self.env["account.report.line"]
        imd = self.env["ir.model.data"]

        def _create_report(report_name, line_names):
            """
            Create new report and its lines from `line_names` list.

            Examples of line_names (and the resulting report structure):
              * std_a
                * cus_a_1 (child of std_a)
                  * cus_a_1_i
                  * cus_a_1_ii (sibling of cus_a_i_i)
                * std_a_2
              * cus_b
            Important: lines `sequence` and `parent_id` values will be inferred from the order of the provided line_names.
            """
            report = ar.create({"name": report_name})
            imd.create(
                {
                    "module": "test_upg",
                    "name": "upg_test_account_report_" + report_name,
                    "model": "account.report",
                    "res_id": report.id,
                }
            )

            last_line_id_by_level = {-1: False}  # base case for root level lines
            for idx, line_name in enumerate(line_names, start=1):
                std_flag, *name = line_name.split("_")

                line_hierarchy_level = 1 + 2 * len(name[1:])
                parent_id = last_line_id_by_level[line_hierarchy_level - 2]
                line = arl.create(
                    {
                        "name": line_name,
                        "parent_id": parent_id,
                        "report_id": report.id,
                        "hierarchy_level": line_hierarchy_level,
                        "sequence": 10 * idx,
                    }
                )
                last_line_id_by_level[line_hierarchy_level] = line.id
                if std_flag == "std":
                    imd.create(
                        {
                            "module": "test_upg",
                            "name": "upg_test_account_report_line_{}_{}".format(line_name, report_name),
                            "model": "account.report.line",
                            "res_id": line.id,
                        }
                    )

            return report

        # in the following, every report is meant to test some aspects of the resequencing process
        # the following maps those reports to the expected order of lines after the upgrade
        post_upg_expected_lines_order = {}

        # Report 1
        #   Change: new standard line is introduced
        #   Desired outcome: top custom sibling is still listed before the new standard line
        #                    custom sibling subtree is unmodified
        report_1 = _create_report(
            "r1",
            [
                "cus_a",
                "cus_a_1",
                "cus_a_2",
                "cus_a_3",
                "cus_a_3_i",
                "cus_a_3_ii",
                "std_b",
            ],
        )
        post_upg_expected_lines_order[report_1.id] = [
            "cus_a",
            "cus_a_1",
            "cus_a_2",
            "cus_a_3",
            "cus_a_3_i",
            "cus_a_3_ii",
            "std_z",
            "std_b",
        ]

        # Report 2
        #   Change: standard lines are swapped
        #   Desired outcome: custom lines are swapped too (following their closest, preceding standard sibling)
        report_2 = _create_report(
            "r2",
            [
                "std_a",
                "cus_b",
                "cus_c",
                "std_d",
                "cus_e",
                "cus_f",
            ],
        )
        post_upg_expected_lines_order[report_2.id] = [
            "std_d",
            "cus_e",
            "cus_f",
            "std_a",
            "cus_b",
            "cus_c",
        ]

        # Report 3
        #   Change: standard line is removed
        #   Desired outcome: relative order of other (custom and standard) is not affected
        report_3 = _create_report(
            "r3",
            [
                "std_a",
                "cus_b",
                "std_c",
            ],
        )
        post_upg_expected_lines_order[report_3.id] = [
            "cus_b",
            "std_c",
        ]

        # Report 4
        #   Change:  standard parent line is removed
        #   Desired outcome: custom children become top-level lines and retain the relative order (wrt other top-level lines)
        report_4 = _create_report(
            "r4",
            [
                "std_a",
                "std_b",
                "std_b_1",
                "cus_b_2",
                "cus_b_3",
                "cus_b_3_i",
                "std_c",
            ],
        )
        post_upg_expected_lines_order[report_4.id] = [
            "std_a",
            "cus_b_2",
            "cus_b_3",
            "cus_b_3_i",
            "std_c",
        ]

        # Report 5
        #   Change:  standard parent line is removed
        #   Desired outcome: custom children become top-level lines and retain the relative order (wrt other top-level lines)
        #   Note: same as report 4, at a nested level
        report_5 = _create_report(
            "r5",
            [
                "std_a",
                "std_b",
                "std_b_1",
                "cus_b_1_i",
                "cus_b_1_i_1",
                "cus_b_1_ii",
                "std_b_2",
                "std_c",
            ],
        )
        post_upg_expected_lines_order[report_5.id] = [
            "std_a",
            "std_b",
            "std_b_2",
            "cus_b_1_i",  # notice: sequenced after std_b_2 because they are not sibling
            "cus_b_1_i_1",
            "cus_b_1_ii",
            "std_c",
        ]

        # Report 6
        #   Change: standard line is removed and its child line is moved to another (standard) parent line
        #   Desired outcome: The whole subtree of the moved line preserves its internal order
        report_6 = _create_report(
            "r6",
            [
                "std_a",
                "std_a_1",
                "cus_a_2",
                "std_b",
                "std_c",
                "std_c_1",
                "std_c_1_i",
                "cus_c_1_ii",
            ],
        )
        post_upg_expected_lines_order[report_6.id] = [
            "std_a",
            "std_c_1",
            "std_c_1_i",
            "cus_c_1_ii",
            "std_a_1",
            "cus_a_2",
            "std_b",
        ]

        return post_upg_expected_lines_order

    def check(self, post_upg_expected_lines_order):
        if not version_gte("17.0"):
            return

        ar = self.env["account.report"]
        for report_id, expected_line_order in post_upg_expected_lines_order.items():
            report = ar.browse(report_id)
            for idx, line in enumerate(report.line_ids):
                self.assertEqual(
                    line.name,
                    expected_line_order[idx],
                    "Expected line {!r} of report {!r} to be at position {}.".format(
                        expected_line_order[idx], report.name, idx
                    ),
                )
