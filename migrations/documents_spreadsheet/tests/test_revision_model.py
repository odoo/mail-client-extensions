# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.5")
class TestSpreadsheetRevisionModel(UpgradeCase):
    def prepare(self):
        folder = self.env["documents.folder"].create({"name": "folder"})
        document = self.env["documents.document"].create({"folder_id": folder.id})
        revision = self.env["spreadsheet.revision"].create(
            [
                {
                    "document_id": document.id,
                    "commands": "",
                    "parent_revision_id": "A",
                    "revision_id": "B",
                },
            ]
        )
        return (revision.id, document.id)

    def check(self, init):
        revision_id, document_id = init
        revision = self.env["spreadsheet.revision"].browse(revision_id)
        self.assertEqual(revision.res_model, "documents.document")
        self.assertEqual(revision.res_id, document_id)
