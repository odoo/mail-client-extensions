import ast
from datetime import timedelta

from odoo import fields

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestShareMigration(UpgradeCase):
    def prepare(self):
        if not util.version_gte("saas~17.4"):
            # TODO: is that correct ?
            # fail on the runbot, see https://runbot.odoo.com/runbot/build/68372144
            return None

        Folder = self.env["documents.folder"]
        Document = self.env["documents.document"]
        Share = self.env["documents.share"]
        Facet = self.env["documents.facet"]
        Tag = self.env["documents.tag"]
        User = self.env["res.users"]

        companies = self.env["res.company"].create([{"name": "Company 1"}, {"name": "Company 2"}])

        # to check that the XMLID has been changed
        self.env.ref("documents.documents_internal_folder").name = "INTERNAL FOLDER"
        internal_user = self.env.ref("base.group_user")
        system_user = self.env.ref("base.group_system")
        other_group = self.env["res.groups"].create({"name": "Other group"})
        activity_type_todo = self.env.ref("mail.mail_activity_data_todo")

        admins = User.create(
            [
                {
                    "name": f"admin {i}",
                    "login": f"admin {i}",
                    "groups_id": system_user.ids,
                }
                for i in range(2)
            ]
        )

        internals = User.create(
            [
                {
                    "name": f"internal {i}",
                    "login": f"internal {i}",
                    "groups_id": (internal_user | other_group).ids,
                }
                for i in range(2)
            ]
        )

        f_level0 = Folder.create(
            [
                {
                    "name": "Folder A",
                    "group_ids": system_user.ids,
                    "read_group_ids": system_user.ids,
                    "company_id": companies[0].id,
                },
                {
                    "name": "Folder B",
                    "group_ids": system_user.ids,
                    "company_id": companies[1].id,
                },
                {"name": "Folder C"},
            ]
        )

        f_level1 = Folder.create(
            [
                {"parent_folder_id": f_level0[0].id, "name": "Folder A A"},
                {"parent_folder_id": f_level0[1].id, "name": "Folder B A"},
                {
                    "parent_folder_id": f_level0[1].id,
                    "name": "Folder B B",
                    "company_id": companies[0].id,
                },
            ]
        )

        f_level2 = Folder.create(
            [
                {
                    "parent_folder_id": f_level1[0].id,
                    "name": "Folder A A A",
                    "company_id": companies[1].id,  # the company changed here
                },
                {"parent_folder_id": f_level1[0].id, "name": "Folder A A B"},
                {"parent_folder_id": f_level1[2].id, "name": "Folder B B A"},
                {"parent_folder_id": f_level1[2].id, "name": "Folder B B B"},
                {
                    "parent_folder_id": f_level1[2].id,
                    "name": "Folder B B C",
                    "user_specific": True,
                },
                {
                    "parent_folder_id": f_level1[2].id,
                    "name": "Folder B B D",
                    "user_specific": True,
                    "user_specific_write": True,
                },
                {
                    # only read_group_ids is propagated to the children
                    # group_ids has only effect on the folder, not on the files inside of it
                    "parent_folder_id": f_level1[2].id,
                    "name": "Folder B B E",
                    "group_ids": other_group.ids,
                    "read_group_ids": system_user.ids,
                },
            ]
        )

        documents = Document.create(
            [
                {"folder_id": f_level0[0].id, "name": "A - DOC"},
                {"folder_id": f_level0[2].id, "name": "C - DOC"},
                {"folder_id": f_level0[1].id, "name": "B - DOC"},
                {"folder_id": f_level1[0].id, "name": "A A - DOC 1"},
                {"folder_id": f_level1[0].id, "name": "A A - DOC 2"},
                {"folder_id": f_level2[0].id, "name": "A A A - DOC"},
                {"folder_id": f_level2[3].id, "name": "B B B - DOC"},
                {  # user specific
                    "folder_id": f_level2[4].id,
                    "name": "B B C - DOC",
                    "owner_id": internals[1].id,
                },
                {  # user specific
                    "folder_id": f_level2[4].id,
                    "name": "B B C - DOC",
                    "owner_id": internals[0].id,
                },
                {  # user specific write
                    "folder_id": f_level2[5].id,
                    "name": "B B D - DOC",
                    "owner_id": internals[0].id,
                },
                {
                    "folder_id": f_level2[6].id,
                    "name": "Test group",
                },
            ]
        )

        facets = Facet.create(
            [
                {"folder_id": f_level2[0].id, "name": "Folder A A A - Facet"},
                {"folder_id": f_level0[1].id, "name": "Folder B - Facet"},
            ]
        )

        tags = Tag.create(
            [
                {"facet_id": facets[0].id, "name": "Tag 1"},
                {"facet_id": facets[1].id, "name": "Tag A"},
                {"facet_id": facets[0].id, "name": "Tag 2"},
                {"facet_id": facets[0].id, "name": "Tag 3"},
                # name already set on facet 0
                {"facet_id": facets[1].id, "name": "Tag 1"},
                {"facet_id": facets[1].id, "name": "Tag 3"},
            ]
        )

        self.env["res.lang"]._activate_lang("fr_FR")
        facets[0].with_context(lang="fr_FR").name = "Facet FR A A A"
        tags[0].with_context(lang="fr_FR").name = "FR 1"
        # will have a mix of French and English
        tags[1].with_context(lang="fr_FR").name = "FR 2"

        documents[0].tag_ids = tags[1] | tags[2] | tags[3] | tags[4] | tags[5]

        # Share simple document
        def _share_document(document):
            return Share.with_context(**document.create_share()["context"]).create({})

        share_documents = _share_document(documents[0])
        share_documents |= _share_document(documents[1])
        share_documents |= _share_document(documents[0])

        # Share folders
        share_folders = Share.create(
            [
                {
                    # Allow writing
                    "name": "Share",
                    "folder_id": f_level0[0].id,
                    # include_sub_folders is True by default
                    "allow_upload": True,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level0[0].id]],
                    "alias_name": "alias-1",
                    "activity_option": True,
                    "activity_type_id": activity_type_todo.id,
                    "activity_summary": "Summary: Folder A",
                    "activity_note": "Note: Folder A",
                    "activity_date_deadline_range": 1,
                    "activity_date_deadline_range_type": "months",
                    "activity_user_id": internals[0].id,
                },
                {
                    # Allow reading
                    "name": "Share",
                    "folder_id": f_level0[0].id,
                    "include_sub_folders": True,
                    "allow_upload": False,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level0[0].id]],
                    "alias_name": "alias-2",
                },
                {
                    # Allow reading (no sub folder)
                    "name": "Share",
                    "folder_id": f_level1[2].id,
                    "include_sub_folders": True,
                    "allow_upload": False,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level1[2].id]],
                    "alias_name": "alias-3",
                },
                {
                    # Ignored because impossible with the new implementation
                    "name": "Share",
                    "folder_id": f_level1[1].id,
                    "allow_upload": True,
                    "include_sub_folders": False,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level1[1].id]],
                },
                # for alias check
                {
                    "name": "Share",
                    "folder_id": f_level0[0].id,
                    "allow_upload": True,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level0[0].id]],
                    "alias_name": "alias-4",
                    "tag_ids": tags.ids,
                },
                {
                    "name": "Share",
                    "folder_id": f_level0[0].id,
                    "allow_upload": True,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level0[0].id]],
                    "alias_name": "alias-5",
                    # Tags [0, 4] and [3, 5] have the same name
                    # Keep only the first one
                    "tag_ids": (tags[1] | tags[2] | tags[3] | tags[4] | tags[5]).ids,
                },
                {
                    "name": "Share",
                    "folder_id": f_level0[0].id,
                    "allow_upload": True,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level0[0].id]],
                    "alias_name": "alias-6",
                },
                {
                    # Share with create activity that will be transmitted on the folder
                    "name": "Share",
                    "folder_id": f_level2[1].id,
                    "allow_upload": True,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level2[1].id]],
                    "alias_name": "alias-8",
                    "activity_option": True,
                    "activity_type_id": activity_type_todo.id,
                    "activity_summary": "Summary: Folder A A B",
                    "activity_note": "Note: Folder A A B",
                    "activity_date_deadline_range": 9,
                    "activity_date_deadline_range_type": "days",
                    "activity_user_id": internals[1].id,
                },
                {
                    # Share with an expiration date are removed (because there's
                    # no `date_deadline` field, and we don't want to extend the access)
                    "name": "Share",
                    "folder_id": f_level0[0].id,
                    "allow_upload": True,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level0[0].id]],
                    "alias_name": "alias-7",
                    "date_deadline": fields.Date.today() + timedelta(days=4),
                },
            ]
        )

        self.assertTrue(share_folders[0].email_drop)
        self.assertFalse(share_folders[1].email_drop)  # allow_upload is False
        self.assertFalse(share_folders[2].email_drop)  # allow_upload is False
        self.assertFalse(share_folders[3].email_drop)  # no alias_name is set
        self.assertTrue(share_folders[4].email_drop)
        self.assertTrue(share_folders[5].email_drop)

        # Share list of documents
        share_ids = Share.create(
            [
                {
                    "name": "Share A - 1",
                    "folder_id": f_level0[0].id,
                    "include_sub_folders": True,
                    "type": "ids",
                    "document_ids": documents[:3].ids,
                },
            ]
        )

        # Rename of fields in workflow rule
        workflow_rule = self.env["documents.workflow.rule"].create(
            {
                "domain_folder_id": f_level0[1].id,
                "name": "workflow Folder B",
                "folder_id": f_level0[0].id,
                "remove_activities": True,
                "activity_option": True,
                "activity_type_id": activity_type_todo.id,
                "activity_summary": "Test workflow rule activity summary",
                "activity_date_deadline_range": 2,
                "activity_date_deadline_range_type": "months",
                "activity_note": "Test workflow rule activity note",
                "has_owner_activity": True,
                "activity_user_id": internals[0].id,
                "domain": [
                    ("folder_id.name", "=", "test"),
                    "|",
                    ("folder_id", "!=", f_level1[1].id),
                    ("folder_id", "in", (f_level2[0].id, f_level2[2].id)),
                ],
                "tag_action_ids": [
                    [
                        0,
                        0,
                        {
                            "action": "add",
                            "tag_id": tags[0].id,
                            "facet_id": tags[0].facet_id.id,
                        },
                    ],
                    [
                        0,
                        0,
                        {
                            "action": "replace",
                            "tag_id": tags[1].id,
                            "facet_id": tags[1].facet_id.id,
                        },
                    ],
                    [
                        0,
                        0,
                        {
                            "action": "replace",
                            "tag_id": tags[0].id,
                            "facet_id": tags[0].facet_id.id,
                        },
                    ],
                ],
            }
        )

        return {
            "documents": documents.ids,
            "tags": tags.ids,
            "workflow_rules": workflow_rule.ids,
            # Shares
            "share_documents": [share.access_token for share in share_documents],
            "share_folders": [share.access_token for share in share_folders],
            "share_ids": [share.access_token for share in share_ids],
            "users_admins": admins.ids,
            "users_internals": internals.ids,
            "alias_ids": share_folders.alias_id.ids,
            "companies_ids": companies.ids,
        }

    def check(self, init):
        if not init:
            return

        documents = self.env["documents.document"].browse(init["documents"])
        tags = self.env["documents.tag"].browse(init["tags"])
        users_admins = self.env["res.users"].browse(init["users_admins"])
        users_internals = self.env["res.users"].browse(init["users_internals"])
        activity_type_todo = self.env.ref("mail.mail_activity_data_todo")

        self.env["documents.access"].search(
            [("partner_id", "not in", (users_admins | users_internals).partner_id.ids)]
        ).unlink()

        #################
        # CHECK FOLDERS #
        #################

        f_level0 = self.env["documents.document"].search(
            [("name", "=like", "Folder _")],
            order="name",
        )
        self.assertEqual(len(f_level0), 3)
        self.assertEqual(f_level0.mapped("name"), ["Folder A", "Folder B", "Folder C"])
        self.assertTrue(not any(f_level0.mapped("folder_id")))

        f_level1 = self.env["documents.document"].search(
            [("name", "=like", "Folder _ _")],
            order="name",
        )
        self.assertEqual(len(f_level1), 3)
        self.assertEqual(
            f_level1.mapped("name"),
            ["Folder A A", "Folder B A", "Folder B B"],
        )
        self.assertEqual(f_level1[0].folder_id, f_level0[0])
        self.assertEqual(f_level1[1].folder_id, f_level0[1])
        self.assertEqual(f_level1[2].folder_id, f_level0[1])

        f_level2 = self.env["documents.document"].search(
            [("name", "=like", "Folder _ _ _")],
            order="name",
        )
        self.assertEqual(len(f_level2), 7)
        self.assertEqual(
            f_level2.mapped("name"),
            [
                "Folder A A A",
                "Folder A A B",
                "Folder B B A",
                "Folder B B B",
                "Folder B B C",
                "Folder B B D",
                "Folder B B E",
            ],
        )
        self.assertEqual(f_level2[0].folder_id, f_level1[0])
        self.assertEqual(f_level2[1].folder_id, f_level1[0])
        self.assertEqual(f_level2[2].folder_id, f_level1[2])
        self.assertEqual(f_level2[3].folder_id, f_level1[2])
        self.assertEqual(f_level2[4].folder_id, f_level1[2])
        self.assertEqual(f_level2[5].folder_id, f_level1[2])

        self.assertEqual(documents[0].folder_id, f_level0[0])
        self.assertEqual(documents[1].folder_id, f_level0[2])
        self.assertEqual(documents[2].folder_id, f_level0[1])
        self.assertEqual(documents[3].folder_id, f_level1[0])
        self.assertEqual(documents[4].folder_id, f_level1[0])
        self.assertEqual(documents[5].folder_id, f_level2[0])
        self.assertEqual(documents[6].folder_id, f_level2[3])
        self.assertEqual(documents[7].folder_id, f_level2[4])

        folder_parent_path = [  # documents.parent_path
            f"{f_level0[0].id}/",
            f"{f_level0[2].id}/",
            f"{f_level0[1].id}/",
            f"{f_level0[0].id}/{f_level1[0].id}/",
            f"{f_level0[0].id}/{f_level1[0].id}/",
            f"{f_level0[0].id}/{f_level1[0].id}/{f_level2[0].id}/",
            f"{f_level0[1].id}/{f_level1[2].id}/{f_level2[3].id}/",
            f"{f_level0[1].id}/{f_level1[2].id}/{f_level2[4].id}/",
            f"{f_level0[1].id}/{f_level1[2].id}/{f_level2[4].id}/",
            f"{f_level0[1].id}/{f_level1[2].id}/{f_level2[5].id}/",
            f"{f_level0[1].id}/{f_level1[2].id}/{f_level2[6].id}/",
        ]
        for doc, folder_path in zip(documents, folder_parent_path, strict=True):
            self.assertEqual(doc.parent_path, f"{folder_path}{doc.id}/")

        folder_parent_path = [  # f_level2.parent_path
            f"{f_level0[0].id}/{f_level1[0].id}/",
            f"{f_level0[0].id}/{f_level1[0].id}/",
            f"{f_level0[1].id}/{f_level1[2].id}/",
            f"{f_level0[1].id}/{f_level1[2].id}/",
            f"{f_level0[1].id}/{f_level1[2].id}/",
            f"{f_level0[1].id}/{f_level1[2].id}/",
            f"{f_level0[1].id}/{f_level1[2].id}/",
        ]
        for doc, folder_path in zip(f_level2, folder_parent_path, strict=True):
            self.assertEqual(doc.parent_path, f"{folder_path}{doc.id}/")

        folder_parent_path = [  # f_level1.parent_path
            f"{f_level0[0].id}/",
            f"{f_level0[1].id}/",
            f"{f_level0[1].id}/",
        ]
        for doc, folder_path in zip(f_level1, folder_parent_path, strict=True):
            self.assertEqual(doc.parent_path, f"{folder_path}{doc.id}/")

        for folder in f_level0:
            self.assertEqual(folder.parent_path, f"{folder.id}/")

        ###############
        # CHECK XMLID #
        ###############
        internal_folder = self.env.ref("documents.document_internal_folder")
        self.assertEqual(internal_folder.name, "INTERNAL FOLDER")
        self.assertFalse(
            self.env.ref(
                "documents.documents_internal_folder",
                raise_if_not_found=False,
            )
        )
        self.assertEqual(internal_folder.access_internal, "edit")

        ################
        # CHECK SHARES #
        ################

        self.assertEqual(f_level0.mapped("is_access_via_link_hidden"), [False] * 3)
        self.assertEqual(f_level0.mapped("access_via_link"), ["view", "none", "none"])
        self.assertEqual(f_level1.mapped("is_access_via_link_hidden"), [False] * 3)
        self.assertEqual(f_level1.mapped("access_via_link"), ["none", "none", "view"])
        self.assertEqual(f_level2.mapped("access_via_link"), ["none", "view"] + ["none"] * 5)
        self.assertEqual(f_level2.mapped("is_access_via_link_hidden"), [False] * 7)

        def _check_document_access(document, user, access):
            document_access = self.env["documents.access"].search(
                [
                    ("document_id", "=", document.id),
                    ("partner_id", "=", user.partner_id.id),
                ]
            )
            if access == "none":
                self.assertFalse(document_access)
            else:
                self.assertEqual(len(document_access), 1)
                self.assertEqual(document_access.role, access)

        _get_redirection = self.env["documents.redirect"]._get_redirection

        # group_ids = system - read_group_ids = system
        _check_document_access(f_level0[0], users_admins[0], "edit")
        _check_document_access(f_level0[0], users_admins[1], "edit")
        _check_document_access(f_level0[0], users_internals[0], "none")

        f_level0_0 = self.env["documents.document"].search([("name", "=", "Folder A")])
        self.assertEqual(len(f_level0_0), 1)
        self.assertEqual(f_level0_0.access_via_link, "view")
        self.assertEqual(
            f_level0_0,
            _get_redirection(init["share_folders"][1]),
        )
        self.assertEqual(
            f_level0_0.access_via_link,
            "view",
            "Remove the edit access if at least one is read access",
            # because other tokens will be redirected to that one, and we
            # don't want to give write access
        )
        self.assertEqual(
            f_level0[0],
            _get_redirection(init["share_folders"][0]),
        )

        f_level1_2 = self.env["documents.document"].search([("name", "=", "Folder B B")])
        self.assertEqual(len(f_level1_2), 1)
        self.assertEqual(
            f_level1_2,
            _get_redirection(init["share_folders"][2]),
        )
        self.assertEqual(f_level1_2.access_via_link, "view")

        # token of a share with include_sub_folders == False
        self.assertFalse(_get_redirection(init["share_folders"][3]))
        self.assertEqual(
            f_level0[0],
            _get_redirection(init["share_folders"][4]),
        )
        self.assertEqual(
            f_level0[0],
            _get_redirection(init["share_folders"][5]),
        )
        self.assertEqual(
            f_level0[0],
            _get_redirection(init["share_folders"][6]),
        )

        # share single document
        self.assertEqual(documents[0].access_via_link, "view")
        self.assertEqual(documents[0], _get_redirection(init["share_documents"][-1]))
        self.assertEqual(
            documents[0],
            _get_redirection(init["share_documents"][0]),
        )
        self.assertEqual(documents[1].access_via_link, "view")
        self.assertEqual(
            documents[1],
            _get_redirection(init["share_documents"][1]),
        )

        # check that share with an expiration date are not migrated
        self.assertFalse(self.env["documents.document"].search([("document_token", "=", init["share_folders"][8])]))
        self.assertFalse(_get_redirection(init["share_folders"][8]))

        # check that no token are copied from the share to the document
        self.assertFalse(self.env["documents.document"].search([("document_token", "in", init["share_documents"])]))

        tokens = self.env["documents.document"].search([]).mapped("document_token")
        self.assertEqual(len(tokens), len(set(tokens)), "All tokens should be unique")

        ##########################
        # CHECK DOCUMENTS.ACCESS #
        ##########################
        self.assertEqual(len(f_level0[0].access_ids), 2)
        self.assertEqual(f_level0[0].access_ids.mapped("role"), ["edit"] * 2)
        self.assertEqual(
            f_level0[0].access_ids.mapped("partner_id"),
            users_admins.partner_id,
        )
        self.assertEqual(f_level0[0].access_internal, "none")

        self.assertEqual(len(f_level0[1].access_ids), 2)
        self.assertEqual(f_level0[1].access_ids.mapped("role"), ["edit"] * 2)
        self.assertEqual(
            f_level0[1].access_ids.mapped("partner_id"),
            users_admins.partner_id,
        )
        self.assertEqual(f_level0[1].access_internal, "none")

        # no group set, internal can read and write
        self.assertFalse(f_level0[2].access_ids)
        self.assertEqual(f_level0[2].access_internal, "edit")

        self.assertFalse(f_level1[0].access_ids)
        self.assertEqual(f_level1[0].access_internal, "edit")

        # check the propagation of the access of the folder on the documents
        self.assertEqual(
            documents[0].access_ids.mapped("partner_id"),
            users_admins.partner_id,
        )
        self.assertEqual(documents[0].access_ids.mapped("role"), ["view"] * 2)

        # only the read_group is propagated, not the write_group
        self.assertEqual(
            documents[10].access_ids.mapped("partner_id"),
            users_admins.partner_id,
        )
        self.assertEqual(documents[10].access_ids.mapped("role"), ["view"] * 2)

        # Check user_specific
        doc_1, doc_2, doc_3 = documents[7], documents[8], documents[9]
        self.assertEqual(doc_1.access_internal, "none")
        self.assertEqual(doc_1.access_via_link, "none")
        self.assertEqual(doc_2.access_internal, "none")
        self.assertEqual(doc_2.access_via_link, "none")
        self.assertEqual(doc_3.access_internal, "none")
        self.assertEqual(doc_3.access_via_link, "none")

        self.assertEqual(len(doc_1.access_ids), 1)
        self.assertEqual(len(doc_2.access_ids), 1)
        self.assertFalse(
            doc_3.access_ids,
            "user_specific_write is implemented with owner_id",
        )
        self.assertTrue(doc_1.is_access_via_link_hidden)
        self.assertTrue(doc_2.is_access_via_link_hidden)
        self.assertTrue(doc_3.is_access_via_link_hidden)

        self.assertEqual(doc_1.access_ids.partner_id, users_internals[1].partner_id)
        self.assertEqual(doc_2.access_ids.partner_id, users_internals[0].partner_id)

        self.assertEqual(doc_1.access_ids.role, "view")
        self.assertEqual(doc_2.access_ids.role, "view")

        self.assertEqual(doc_1.owner_id, self.env.ref("base.user_root"))
        self.assertEqual(doc_2.owner_id, self.env.ref("base.user_root"))
        self.assertEqual(doc_3.owner_id, users_internals[0])

        ###############
        # CHECK ALIAS #
        ###############

        alias_ids = self.env["mail.alias"].browse(init["alias_ids"])
        self.assertTrue(alias_ids[0].exists())
        self.assertFalse(alias_ids[1].alias_name)  # allow_upload was False
        self.assertFalse(alias_ids[2].alias_name)  # allow_upload was False
        self.assertFalse(alias_ids[3].exists())  # this config can not be migrated
        self.assertTrue(alias_ids[4].exists())
        self.assertTrue(alias_ids[5].exists())
        self.assertTrue(alias_ids[6].exists())
        self.assertTrue(alias_ids[7].exists())

        # Check that no document has create_activity except "Folder A A B"
        for doc in documents + f_level0 + f_level1 + f_level2:
            if doc.name != "Folder A A B":
                self.assertFalse(doc.create_activity_option)

        # the alias with tag should have the priority
        self.assertEqual(
            f_level0[0].alias_id,
            alias_ids[5],
            "The share with tags must have the priority, then the most recent one",
        )

        self.assertTrue(all(alias.alias_parent_model_id.model == "documents.document" for alias in alias_ids.exists()))
        self.assertTrue(
            all(
                alias.alias_parent_thread_id in (f_level0[0].id, f_level2[1].id)
                for alias in alias_ids.exists()
                if alias.alias_name
            )
        )

        # the tag of the mail alias must be on `alias_tag_ids` on <documents.document>
        defaults = ast.literal_eval(alias_ids[5].alias_defaults)
        self.assertTrue("tag_ids" not in defaults)
        self.assertEqual(defaults["folder_id"], f_level0[0].id)

        defaults = ast.literal_eval(alias_ids[0].alias_defaults)
        self.assertTrue("tag_ids" not in defaults)
        self.assertEqual(defaults["folder_id"], f_level0[0].id)

        # create_activity on alias and related document
        self.assertEqual(
            {field: value for field, value in defaults.items() if field.startswith("create_activity_")},
            {
                "create_activity_option": True,
                "create_activity_type_id": activity_type_todo.id,
                "create_activity_summary": "Summary: Folder A",
                "create_activity_note": "<p>Note: Folder A</p>",
                "create_activity_date_deadline_range": 1,
                "create_activity_date_deadline_range_type": "months",
                "create_activity_user_id": users_internals[0].id,
            },
        )
        self.assertFalse(f_level0[0].create_activity_option)

        defaults = ast.literal_eval(alias_ids[4].alias_defaults)
        self.assertEqual(
            sorted(defaults["tag_ids"][0][2]),
            sorted((tags[1] | tags[2] | tags[3] | tags[0]).ids),
            "tags[5] has a duplicated name, should have been removed, tags[4] should be mapped to tags[0]",
        )
        self.assertEqual(defaults["folder_id"], f_level0[0].id)

        defaults = ast.literal_eval(alias_ids[6].alias_defaults)
        self.assertTrue("tag_ids" not in defaults)
        self.assertEqual(defaults["folder_id"], f_level0[0].id)

        defaults = ast.literal_eval(alias_ids[7].alias_defaults)
        self.assertFalse(any(field.startswith("create_activity_") for field in defaults))
        self.assertTrue(f_level2[1].create_activity_option)
        self.assertEqual(f_level2[1].create_activity_type_id, activity_type_todo)
        self.assertEqual(f_level2[1].create_activity_summary, "Summary: Folder A A B")
        self.assertEqual(f_level2[1].create_activity_note, "<p>Note: Folder A A B</p>")
        self.assertEqual(f_level2[1].create_activity_date_deadline_range, 9)
        self.assertEqual(f_level2[1].create_activity_date_deadline_range_type, "days")
        self.assertEqual(f_level2[1].create_activity_user_id, users_internals[1])
        self.assertEqual(f_level0[0].alias_name, "alias-5")

        ##############
        # CHECK TAGS #
        ##############
        self.assertEqual(tags.exists(), tags[0] | tags[1] | tags[2] | tags[3], "Should have removed duplicated tags")

        self.assertEqual(
            f_level0[0].alias_tag_ids,
            tags[1] | tags[2] | tags[3] | tags[0],
            "tags[5] has a duplicated name, should have been removed, tags[4] should be mapped to tags[0]",
        )
        self.assertEqual(
            documents[0].tag_ids,
            tags[1] | tags[2] | tags[3] | tags[0],
            "tags[5] has a duplicated name, should have been removed, tags[4] should be mapped to tags[0]",
        )

        ###################
        # CHECK COMPANIES #
        ###################
        companies = self.env["res.company"].browse(init["companies_ids"])

        self.assertEqual(f_level0[0].company_id, companies[0])
        self.assertEqual(f_level0[1].company_id, companies[1])
        # no folder above with a company to fix it
        self.assertFalse(f_level0[2].company_id)

        self.assertEqual(f_level1[0].company_id, companies[0])
        self.assertEqual(f_level1[1].company_id, companies[1])
        self.assertEqual(f_level1[2].company_id, companies[0])

        self.assertEqual(f_level2[0].company_id, companies[1])
        self.assertEqual(f_level2[1].company_id, companies[0])
        self.assertEqual(f_level2[2].company_id, companies[0])
        self.assertEqual(f_level2[3].company_id, companies[0])

        self.assertEqual(documents[0].company_id, companies[0])
        self.assertFalse(documents[1].company_id)  # f_level0[2] has no company
        # inherit from f_level2[0]
        self.assertEqual(documents[5].company_id, companies[1])
