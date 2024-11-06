from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestShareMigration(UpgradeCase):
    def prepare(self):
        """Check that documents manager can not read others payslips after the upgrade."""
        user_1 = self.env["res.users"].create(
            {
                "name": "Test HR 1",
                "login": "test_hr_1",
                "groups_id": [(6, 0, [self.env.ref("documents.group_documents_manager").id])],
            }
        )
        user_2 = self.env["res.users"].create(
            {
                "name": "Test HR 2",
                "login": "test_hr_2",
                "groups_id": [(6, 0, [self.env.ref("documents.group_documents_manager").id])],
            }
        )

        user_3 = self.env["res.users"].create(
            {
                "name": "Test HR 3",
                "login": "test_hr_3",
                "groups_id": [
                    (6, 0, [self.env.ref("hr.group_hr_user").id, self.env.ref("documents.group_documents_manager").id])
                ],
            }
        )

        folder = self.env["documents.folder"].create(
            {
                "name": "HR",
                "group_ids": [(4, self.env.ref("hr.group_hr_user").id)],
                "read_group_ids": [(4, self.env.ref("base.group_user").id)],
                "user_specific": True,
            }
        )
        document_1 = self.env["documents.document"].create(
            {
                "name": "d1",
                "folder_id": folder.id,
                "owner_id": user_1.id,
                "partner_id": user_1.partner_id.id,
                "datas": "ZGF0YQ==",
                "res_model": "hr.payslip",
            }
        )

        return {
            "user_1": user_1.id,
            "user_2": user_2.id,
            "user_3": user_3.id,
            "document_1": document_1.id,
        }

    def check(self, init):
        user_1 = self.env["res.users"].browse(init["user_1"])
        user_2 = self.env["res.users"].browse(init["user_2"])
        user_3 = self.env["res.users"].browse(init["user_3"])
        document_1 = self.env["documents.document"].browse(init["document_1"])

        access = {a.partner_id: a.role for a in document_1.access_ids}
        self.assertEqual(
            access.get(user_1.partner_id),
            "view",
            "He was the owner, he's in the read group but not in the write group",
        )
        self.assertEqual(access.get(user_2.partner_id), None)
        self.assertEqual(access.get(user_3.partner_id), "edit")

        access = {a.partner_id: a.role for a in document_1.folder_id.access_ids}
        self.assertEqual(access.get(user_1.partner_id), None)
        self.assertEqual(access.get(user_2.partner_id), None)
        self.assertEqual(access.get(user_3.partner_id), "edit")

        self.assertTrue(document_1.with_user(user_1).has_access("read"))
        self.assertFalse(document_1.with_user(user_2).has_access("read"))
        self.assertTrue(document_1.with_user(user_3).has_access("read"))
        self.assertTrue(document_1.with_user(user_3).has_access("write"))

        # User specific folder is accessible only for HR users
        self.assertFalse(document_1.folder_id.with_user(user_1).has_access("read"))
        self.assertFalse(document_1.folder_id.with_user(user_1).has_access("write"))
        self.assertFalse(document_1.folder_id.with_user(user_2).has_access("read"))
        self.assertFalse(document_1.folder_id.with_user(user_2).has_access("write"))
        self.assertTrue(document_1.folder_id.with_user(user_3).has_access("read"))
        self.assertTrue(document_1.folder_id.with_user(user_3).has_access("write"))

        self.assertEqual(document_1.access_internal, "none")
        self.assertEqual(document_1.folder_id.access_internal, "none")
        self.assertTrue(document_1.is_access_via_link_hidden)
