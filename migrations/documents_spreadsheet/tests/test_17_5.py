import base64
import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestSpreadsheetShareMigration(UpgradeCase):
    def prepare(self):
        def get_frozen_spreadsheet_vals(spreadsheet_shares_vals):
            if util.version_gte("saas~17.4"):
                return {"spreadsheet_shares": json.dumps(spreadsheet_shares_vals)}
            return {
                "freezed_spreadsheet_ids": self.env["documents.share"]._create_spreadsheet_share_commands(
                    spreadsheet_shares_vals
                )
            }

        folders = self.env["documents.folder"].create(
            [
                {"name": "Spreadsheet_main"},
                {"name": "Spreadsheet_other"},
            ]
        )

        spreadsheets = self.env["documents.document"].create(
            [
                {
                    "name": "spreadsheet",
                    "handler": "spreadsheet",
                    "folder_id": folder.id,
                    "spreadsheet_binary_data": base64.b64encode(json.dumps({"test": "data"}).encode()).decode(),
                    "is_multipage": False,
                }
                for folder in folders
            ]
        )

        spreadsheet_shares = [
            {
                "excel_files": [],
                "spreadsheet_data": json.dumps({"test": "data A"}),
                "document_id": spreadsheets[0].id,
            }
        ]

        share_single_doc_1 = self.env["documents.share"].create(
            {
                "document_ids": [(6, 0, spreadsheets[0].ids)],
                "folder_id": spreadsheets[0].folder_id.id,
                "type": "ids",
            }
            | get_frozen_spreadsheet_vals(spreadsheet_shares)
        )

        spreadsheet_shares = [
            {
                "excel_files": [],
                "spreadsheet_data": json.dumps({"test": "data B"}),
                "document_id": spreadsheets[1].id,
            }
        ]

        share_single_doc_2 = self.env["documents.share"].create(
            {
                "document_ids": [(6, 0, spreadsheets[1].ids)],
                "folder_id": spreadsheets[1].folder_id.id,
                "type": "ids",
            }
            | get_frozen_spreadsheet_vals(spreadsheet_shares)
        )

        self.assertEqual(len(share_single_doc_2.freezed_spreadsheet_ids), 1)

        spreadsheet_shares = [
            {
                "excel_files": [],
                "spreadsheet_data": json.dumps({"test": f"data {i}"}),
                "document_id": spreadsheet.id,
            }
            for i, spreadsheet in enumerate(spreadsheets)
        ]

        share_two_docs = self.env["documents.share"].create(
            {
                "type": "domain",
                "folder_id": folders[0].id,
                "domain": repr([("id", "in", spreadsheets.ids)]),
                "document_ids": spreadsheets.ids,
            }
            | get_frozen_spreadsheet_vals(spreadsheet_shares)
        )
        self.assertEqual(len(share_two_docs.freezed_spreadsheet_ids), 2)

        company = self.env["res.company"].create(
            {
                "name": "Test Company",
                "documents_spreadsheet_folder_id": folders[1].id,
            }
        )

        return {
            "share_single_doc_1": share_single_doc_1.access_token,
            "share_single_doc_2": share_single_doc_2.access_token,
            "share_two_docs": share_two_docs.access_token,
            "company": company.id,
        }

    def check(self, init):
        if not init:
            return

        Document = self.env["documents.document"]
        share_single_doc_1_token = init["share_single_doc_1"]
        share_single_doc_2_token = init["share_single_doc_2"]
        share_two_docs_token = init["share_two_docs"]

        # Check that the old tokens are not on the `documents.document`
        result = self.env["documents.document"].search(
            [
                (
                    "document_token",
                    "in",
                    (
                        share_single_doc_1_token,
                        share_single_doc_2_token,
                        share_two_docs_token,
                    ),
                )
            ]
        )
        self.assertFalse(result)

        # Check that no standard spreadsheets are in the `documents_redirect` table
        spreadsheets = self.env["documents.document"].search([("handler", "=", "spreadsheet")])
        self.assertFalse(self.env["documents.redirect"].search([("document_id", "in", spreadsheets.ids)]))

        _get_redirection = self.env["documents.redirect"]._get_redirection

        frozen_folders = Document.search([("name", "=", "Frozen spreadsheets")])
        self.assertEqual(len(frozen_folders), 2)
        for frozen_folder in frozen_folders:
            self.assertTrue(frozen_folder.active)
            self.assertEqual(frozen_folder.handler, "frozen_folder")
            self.assertEqual(frozen_folder.access_via_link, "none")
            self.assertEqual(frozen_folder.access_internal, "view")
            self.assertEqual(frozen_folder.parent_path, f"{frozen_folder.folder_id.parent_path}{frozen_folder.id}/")
        self.assertEqual(
            set(frozen_folders.mapped("folder_id.name")),
            {"Spreadsheet_main", "Spreadsheet_other"},
        )
        self.assertEqual(Document.search_count([("handler", "=", "frozen_folder")]), 2)

        self.assertFalse(_get_redirection(share_two_docs_token))
        document_1 = _get_redirection(share_single_doc_1_token)
        self.assertEqual(len(document_1), 1)
        self.assertEqual(document_1.handler, "frozen_spreadsheet")
        self.assertEqual(document_1.attachment_id.name, "Frozen: spreadsheet")
        self.assertEqual(base64.b64decode(document_1.datas), b'{"test": "data A"}')
        self.assertEqual(document_1.excel_export, b"UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA==")
        self.assertEqual(document_1.spreadsheet_data, json.dumps({"test": "data A"}))
        self.assertIn(document_1.folder_id, frozen_folders)
        self.assertEqual(document_1.parent_path, f"{document_1.folder_id.parent_path}{document_1.id}/")

        document_2 = _get_redirection(share_single_doc_2_token)
        self.assertEqual(len(document_2), 1)
        self.assertEqual(document_2.handler, "frozen_spreadsheet")
        self.assertEqual(document_2.attachment_id.name, "Frozen: spreadsheet")
        self.assertEqual(base64.b64decode(document_2.datas), b'{"test": "data B"}')
        self.assertEqual(document_2.spreadsheet_data, json.dumps({"test": "data B"}))
        self.assertIn(document_2.folder_id, frozen_folders)
        self.assertEqual(document_2.parent_path, f"{document_2.folder_id.parent_path}{document_2.id}/")

        company = self.env["res.company"].browse(init["company"])
        self.assertEqual(
            company.document_spreadsheet_folder_id.name,
            "Spreadsheet_other",
        )
