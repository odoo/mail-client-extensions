from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestExportToDoc(UpgradeCase):
    def prepare(self):
        export_test_cases = [
            (
                datetime(2025, 7, 25, 16, 14, 46, 932966),
                [
                    "Report_07/2025_reimbursement_0",
                    "Report_07/2025_reimbursement_1",
                    "Report_07/2025",
                ],
            ),
            (
                datetime(2025, 7, 25, 18, 36, 13, 123),
                [
                    "Report_07/2025_reimbursement_0",
                    "Report_07/2025",
                ],
            ),
            (
                datetime(2025, 8, 2, 10, 30, 0, 0),
                [
                    "Report_08/2025_reimbursement_0",
                    "Report_08/2025",
                ],
            ),
        ]

        exports = []
        for export_date, export_names in export_test_cases:
            export_ids = []
            attachment_names = []
            with freeze_time(export_date), patch.object(self.env.cr, "now", datetime.now):
                for export_name in export_names:
                    attachment = self.env["ir.attachment"].create(
                        {
                            "name": f"{export_name}.xml",
                            "res_model": "l10n_fr_reports.report",
                            "type": "binary",
                            "raw": b"<report><data>Test Data</data></report>",
                            "mimetype": "application/xml",
                        }
                    )
                    new_export = self.env["account.report.async.export"].create(
                        {
                            "name": export_name,
                            "attachment_ids": attachment.ids,
                            "deposit_uid": "test_deposit_" + export_name,
                            "date_from": "2025-07-01",
                            "date_to": "2025-07-31",
                            "report_id": self.env.ref("l10n_fr_account.tax_report").id,
                            "recipient": False,
                            "state": "sent",
                        }
                    )
                    export_ids.append(new_export.id)
                    attachment_names.append(attachment.name)
            exports.append(
                {
                    "ids": export_ids,
                    "attachment_names": attachment_names,
                    "date": export_date.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        return {
            "exports": exports,
        }

    def check(self, init):
        init_exports = init["exports"]
        init_export_ids = [id_ for export in init_exports for id_ in export["ids"]]

        # Check that (reimbursement) exports were deleted
        exports = self.env["account.report.async.export"].search([("id", "=", init_export_ids)])
        self.assertEqual(len(exports), len(init_exports))

        # Check that new documents records are the same as the initial exports
        documents = self.env["account.report.async.document"].search(
            [("account_report_async_export_id", "=", exports.ids)]
        )
        self.assertEqual(len(documents), len(init_export_ids))

        for init_export in init_exports:
            # Check that there are correct number of documents for each initial export
            documents = self.env["account.report.async.document"].search(
                [("account_report_async_export_id", "=", max(init_export["ids"]))]
            )
            self.assertEqual(len(documents), len(init_export["ids"]))
            self.assertListEqual(documents.mapped("attachment_name"), init_export["attachment_names"])
            self.assertListEqual(
                [create_date.strftime("%Y-%m-%d %H:%M:%S") for create_date in documents.mapped("create_date")],
                [init_export["date"]] * len(documents),
            )

            # Check that the attachments are correctly linked to the documents
            attachments = self.env["ir.attachment"].search(
                [
                    ("res_id", "=", documents.ids),
                    ("res_model", "=", "account.report.async.document"),
                    ("res_field", "=", "attachment"),
                ]
            )
            self.assertEqual(len(attachments), len(documents))
