import ast
import base64
import itertools
from datetime import date, timedelta
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import AccessError

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

ACCOUNT_MOVE_TYPES = ("in_invoice", "out_invoice", "in_refund", "out_refund", "entry", "in_receipt")


@change_version("saas~17.5")
class TestShareMigration(UpgradeCase):
    def prepare(self):
        upload_vals = {
            "allow": {"allow_upload": True} if util.version_gte("saas~17.2") else {"action": "downloadupload"},
            "deny": {"allow_upload": False} if util.version_gte("saas~17.2") else {"action": "download"},
        }

        Folder = self.env["documents.folder"]
        Document = self.env["documents.document"]
        Share = self.env["documents.share"]
        Facet = self.env["documents.facet"]
        Tag = self.env["documents.tag"]
        User = self.env["res.users"]

        companies = self.env["res.company"].create([{"name": "Company UPG1"}, {"name": "Company UPG2"}])

        # to check that the XMLID has been changed
        self.env.ref("documents.documents_internal_folder").name = "INTERNAL FOLDER"
        internal_user = self.env.ref("base.group_user")
        system_user = self.env.ref("base.group_system")
        other_group = self.env["res.groups"].create({"name": "Other group"})
        activity_type_todo = self.env.ref("mail.mail_activity_data_todo")
        activity_type_call = self.env.ref("mail.mail_activity_data_call")

        admins = User.create(
            [
                {
                    "name": f"admin {i}",
                    "login": f"admin {i}",
                    "groups_id": (system_user | internal_user).ids,
                    "company_id": companies[i].id,
                    "company_ids": companies.ids,
                }
                for i in range(2)
            ]
            + [
                {
                    "name": "admin 2",
                    "login": "admin 2",
                    "groups_id": (system_user | internal_user).ids,
                    "company_id": companies[0].id,
                    "company_ids": companies[0].ids,
                }
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
                    "read_group_ids": system_user.ids,
                    "company_id": companies[1].id,
                },
                {"name": "Folder C"},
            ]
        )

        f_level0[0].with_user(admins[2]).check_access_rule("read")
        with self.assertRaises(AccessError):
            f_level0[1].with_user(admins[2]).check_access_rule("read")

        f_level1 = Folder.create(
            [
                {"parent_folder_id": f_level0[0].id, "name": "Folder A A"},
                {"parent_folder_id": f_level0[1].id, "name": "Folder B A"},
                {
                    "parent_folder_id": f_level0[1].id,
                    "name": "Folder B B",
                    "company_id": companies[0].id,
                },
                {"parent_folder_id": f_level0[1].id, "name": "Folder B C"},
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
                    "group_ids": internal_user.ids,
                    "read_group_ids": internal_user.ids,
                },
                {
                    "parent_folder_id": f_level1[2].id,
                    "name": "Folder B B D",
                    "user_specific": True,
                    "user_specific_write": True,
                    "group_ids": internal_user.ids,
                    "read_group_ids": internal_user.ids,
                },
                {
                    "parent_folder_id": f_level1[2].id,
                    "name": "Folder B B E",
                    "group_ids": other_group.ids,
                    "read_group_ids": system_user.ids,
                },
                {
                    # Same but will be shared and not its parent, so it shouldn't be discoverable via link
                    "parent_folder_id": f_level1[3].id,
                    "name": "Folder B C A",
                    "group_ids": other_group.ids,
                    "read_group_ids": system_user.ids,
                },
                {
                    "parent_folder_id": f_level1[3].id,
                    "name": "Folder B C B",
                    "user_specific": True,
                    "user_specific_write": True,
                    "group_ids": system_user.ids,
                    "read_group_ids": internal_user.ids,
                },
            ]
        )

        documents = Document.create(
            [
                {
                    "folder_id": f_level0[0].id,
                    "name": "A - DOC",
                    # folder_id
                    # -> group_ids: other_group
                    # -> read_group_ids: system_user
                    # The owner should be removed to not give him access
                    "owner_id": internals[0].id,
                    "datas": base64.b64encode(b"iVBORw0KGgoAA"),
                    "mimetype": "image/png",
                },
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
                    "partner_id": internals[1].partner_id.id,
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
                    **upload_vals["allow"],
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
                    **upload_vals["deny"],
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level0[0].id]],
                    "alias_name": "alias-2",
                },
                {
                    # Allow reading (no sub folder)
                    "name": "Share",
                    "folder_id": f_level1[2].id,
                    "include_sub_folders": True,
                    **upload_vals["deny"],
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level1[2].id]],
                    "alias_name": "alias-3",
                },
                {
                    # Ignored because impossible with the new implementation
                    "name": "Share",
                    "folder_id": f_level1[1].id,
                    **upload_vals["allow"],
                    "include_sub_folders": False,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level1[1].id]],
                },
                # for alias check
                {
                    "name": "Share",
                    "folder_id": f_level0[0].id,
                    **upload_vals["allow"],
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level0[0].id]],
                    "alias_name": "alias-4",
                    "tag_ids": tags.ids,
                },
                {
                    "name": "Share",
                    "folder_id": f_level0[0].id,
                    **upload_vals["allow"],
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
                    **upload_vals["allow"],
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level0[0].id]],
                    "alias_name": "alias-6",
                },
                {
                    # Share with create activity that will be transmitted on the folder
                    "name": "Share",
                    "folder_id": f_level2[1].id,
                    **upload_vals["allow"],
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
                    **upload_vals["allow"],
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level0[0].id]],
                    "alias_name": "alias-7",
                    "date_deadline": fields.Date.today() + timedelta(days=4),
                },
                {
                    # Check discoverability
                    "name": "Share",
                    "folder_id": f_level2[7].id,
                    "include_sub_folders": True,
                    **upload_vals["deny"],
                    "type": "domain",
                    "domain": [["folder_id", "child_of", f_level2[7].id]],
                    "alias_name": "alias-9",
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
        workflow_rule_base_create = {
            "domain_folder_id": f_level0[0].id,
            "condition_type": "domain",
            "folder_id": f_level0[1].id,
            "remove_activities": True,
            "activity_option": True,
            "activity_type_id": activity_type_todo.id,
            "activity_summary": "Test workflow rule activity summary",
            "activity_date_deadline_range": 2,
            "activity_date_deadline_range_type": "months",
            "activity_note": "Test workflow rule activity note",
            "has_owner_activity": True,
            "activity_user_id": False,
            "tag_action_ids": [
                [
                    0,
                    0,
                    {
                        "action": "replace",
                        "tag_id": tags[0].id,  # add Tag 1
                        "facet_id": tags[0].facet_id.id,  # remove Tag 2&3
                    },
                ],
            ],
        }
        if util.module_installed(self.env.cr, "documents_account"):
            company_id = self.env.company
            cur_id = company_id.currency_id.id
            journal_ids = (
                self.env["account.journal"]
                .create(
                    {
                        "name": "Sale Journal",
                        "code": "MiGraTion18",
                        "type": "sale",
                        "company_id": company_id.id,
                        "currency_id": cur_id,
                    }
                )
                .ids
            )
        else:
            journal_ids = []
        create_workflow_rules = [
            {
                **workflow_rule_base_create,
                "name": "MiGraTion18-Base",
            },
            {
                **workflow_rule_base_create,
                "name": "MiGraTion18-LinkToRecord",
                "create_model": "link.to.record",
                "tag_action_ids": [
                    [
                        0,
                        0,
                        {
                            "action": "remove",
                            "tag_id": tags[0].id,  # remove Tag 1
                            "facet_id": False,
                        },
                    ]
                ],
                "has_owner_activity": False,
                "activity_user_id": internals[0].id,
                "activity_type_id": activity_type_call.id,
            },
            {
                **workflow_rule_base_create,
                "name": "MiGraTion18-LinkToContactRecord",
                "create_model": "link.to.record",
                "link_model": self.env.ref("base.model_res_partner").id,
                "tag_action_ids": [
                    [
                        0,
                        0,
                        {
                            "action": "add",
                            "tag_id": tags[0].id,  # add Tag 1
                            "facet_id": False,
                        },
                    ]
                ],
                "remove_activities": False,
                "has_owner_activity": False,
                "activity_user_id": internals[1].id,
                "activity_date_deadline_range": 3,
                "activity_date_deadline_range_type": "days",
                "folder_id": f_level0[2].id,
            },
        ]
        if util.module_installed(self.env.cr, "documents_account"):
            create_workflow_rules.extend(
                {
                    **workflow_rule_base_create,
                    "name": f"MiGraTion18-Create-account.move-{move_type}",
                    "create_model": f"account.move.{move_type}",
                    "journal_id": journal_ids[0],
                }
                for move_type in ACCOUNT_MOVE_TYPES
            )
            create_workflow_rules.append(
                {
                    **workflow_rule_base_create,
                    "name": "MiGraTion18-Create-account.bank.statement",
                    "create_model": "account.bank.statement",
                    "journal_id": journal_ids[0],
                }
            )
        for create_models, module in (
            (("hr.expense",), "documents_hr_expense"),
            (("hr.applicant",), "documents_hr_recruitment"),
            (("product.template",), "documents_product"),
            (("project.task",), "documents_project"),
            (("sign.template.new", "sign.template.direct"), "documents_sign"),
        ):
            if util.module_installed(self.env.cr, module):
                create_workflow_rules.extend(
                    {
                        **workflow_rule_base_create,
                        "name": f"MiGraTion18-Create-{create_model}",
                        "create_model": create_model,
                    }
                    for create_model in create_models
                )
        # Create workflow rule with criterion (rules are migrated but not pinned)
        create_workflow_rules.extend(
            [
                {
                    **workflow_rule_base_create,
                    "name": f"MiGraTion18-Criterion-{field}",
                    "condition_type": "domain" if field == "domain" else "criteria",
                    field: value,
                }
                for field, value in (
                    ("domain", f"[('owner_id', '=', {internals[0].id})]"),
                    ("criteria_partner_id", internals[0].partner_id.id),
                    ("criteria_owner_id", internals[0].id),
                    ("required_tag_ids", [tags[0].id]),
                    ("excluded_tag_ids", [tags[0].id]),
                )
            ]
        )
        self.env["documents.workflow.rule"].create(create_workflow_rules)

        if util.module_installed(self.env.cr, "documents_account"):
            self.env.cr.execute(
                "SELECT id FROM ir_model_fields WHERE name = 'journal_id' AND model = 'documents.workflow.rule'"
            )
            journal_id_field = self.env.cr.fetchone()[0]
            properties = self.env["ir.property"].search(
                [
                    ("fields_id", "=", journal_id_field),
                    ("value_reference", "=", f"account.journal,{journal_ids[0]}"),
                    ("res_id", "like", "documents.workflow.rule,%"),
                ]
            )
            # There should be one property for each rule (and only for env company)
            self.assertEqual(properties.company_id, self.env.company)
            self.assertEqual(len(properties), len(ACCOUNT_MOVE_TYPES) + 1)

        self.env.cr.execute(
            """
            SELECT ARRAY_AGG(name)
              FROM ir_module_module
             WHERE state = 'installed'
               AND name IN ('documents_hr_expense',
                            'documents_hr_recruitment',
                            'documents_product',
                            'documents_project',
                            'documents_sign')
            """,
        )
        installed_modules = self.env.cr.fetchone()[0] or []

        return {
            "documents": documents.ids,
            "tags": tags.ids,
            # Shares
            "share_documents": [share.access_token for share in share_documents],
            "share_folders": [share.access_token for share in share_folders],
            "share_ids": [share.access_token for share in share_ids],
            "users_admins": admins.ids,
            "users_internals": internals.ids,
            "alias_ids": share_folders.alias_id.ids,
            "companies_ids": companies.ids,
            "journal_ids": journal_ids,
            "installed_modules": installed_modules,
        }

    def check(self, init):
        if not init:
            return

        documents = self.env["documents.document"].browse(init["documents"])
        tags = self.env["documents.tag"].browse(init["tags"])
        users_admins = self.env["res.users"].browse(init["users_admins"])
        users_internals = self.env["res.users"].browse(init["users_internals"])
        activity_type_todo = self.env.ref("mail.mail_activity_data_todo")
        installed_modules = set(init["installed_modules"])

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

        self.assertEqual(f_level0[0].access_ids.mapped("role"), ["edit"] * 3)
        self.assertEqual(f_level0[0].access_ids.mapped("partner_id"), users_admins.partner_id)
        self.assertEqual(f_level0[1].access_ids.mapped("role"), ["edit"] * 2)
        self.assertEqual(f_level0[1].access_ids.mapped("partner_id"), users_admins[:2].partner_id)
        self.assertFalse(f_level0[2].access_ids)

        f_level1 = self.env["documents.document"].search(
            [("name", "=like", "Folder _ _")],
            order="name",
        )
        self.assertEqual(len(f_level1), 4)
        self.assertEqual(
            f_level1.mapped("name"),
            ["Folder A A", "Folder B A", "Folder B B", "Folder B C"],
        )
        self.assertEqual(f_level1[0].folder_id, f_level0[0])
        self.assertEqual(f_level1[1].folder_id, f_level0[1])
        self.assertEqual(f_level1[2].folder_id, f_level0[1])
        self.assertEqual(f_level1[3].folder_id, f_level0[1])

        f_level2 = self.env["documents.document"].search(
            [("name", "=like", "Folder _ _ _")],
            order="name",
        )
        self.assertEqual(len(f_level2), 9)
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
                "Folder B C A",
                "Folder B C B",
            ],
        )
        self.assertEqual(f_level2[0:2].folder_id, f_level1[0])
        self.assertEqual(f_level2[2:5].folder_id, f_level1[2])
        self.assertEqual(f_level2[5:7].folder_id, f_level1[2])
        self.assertEqual(f_level2[7].folder_id, f_level1[3])

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
            f"{f_level0[1].id}/{f_level1[3].id}/",
            f"{f_level0[1].id}/{f_level1[3].id}/",
        ]
        for doc, folder_path in zip(f_level2, folder_parent_path, strict=True):
            self.assertEqual(doc.parent_path, f"{folder_path}{doc.id}/")

        folder_parent_path = [  # f_level1.parent_path
            f"{f_level0[0].id}/",
            f"{f_level0[1].id}/",
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

        self.assertEqual(f_level0.mapped("is_access_via_link_hidden"), [True, False, False])
        self.assertEqual(f_level0.mapped("access_via_link"), ["view", "none", "none"])
        self.assertEqual(f_level1.mapped("is_access_via_link_hidden"), [False] * 4)
        self.assertEqual(f_level1.mapped("access_via_link"), ["view", "none", "view", "none"])
        self.assertEqual(f_level2.mapped("access_via_link"), ["view"] * 8 + ["none"])
        # f_level2[7] is not included in another share and not accessible to internal users -> not discoverable
        self.assertEqual(f_level2.mapped("is_access_via_link_hidden"), [False] * 7 + [True, False])

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
        self.assertEqual(documents[0].folder_id.access_internal, "none")
        self.assertEqual(documents[0].access_internal, "none")
        self.assertEqual(documents[0].access_via_link, "view")
        self.assertEqual(documents[0], _get_redirection(init["share_documents"][-1]))
        self.assertEqual(
            documents[0],
            _get_redirection(init["share_documents"][0]),
        )
        self.assertEqual(documents[0].owner_id, self.env.ref("base.user_root"), "The owner should be reset")
        self.assertEqual(documents[0].partner_id, users_internals[0].partner_id)

        self.assertFalse(documents[0].with_user(users_internals[0]).has_access("read"))
        self.assertEqual(documents[1].access_via_link, "view")
        self.assertEqual(documents[1].folder_id.access_internal, "edit")
        self.assertEqual(documents[1].access_internal, "edit")
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
        self.assertEqual(len(f_level0[0].access_ids), 3)
        self.assertEqual(f_level0[0].access_ids.mapped("role"), ["edit"] * 3)
        self.assertEqual(
            f_level0[0].access_ids.mapped("partner_id"),
            users_admins.partner_id,
        )
        self.assertEqual(f_level0[0].access_internal, "none")

        self.assertEqual(len(f_level0[1].access_ids), 2)
        self.assertEqual(f_level0[1].access_ids.mapped("role"), ["edit"] * 2)
        self.assertEqual(
            f_level0[1].access_ids.mapped("partner_id"),
            users_admins[:2].partner_id,
            "Third admin is not in company 2",
        )
        self.assertEqual(f_level0[1].access_internal, "none")
        self.assertEqual(f_level1[1].access_via_link, "none")

        # no group set, internal can read and write
        self.assertFalse(f_level0[2].access_ids)
        self.assertEqual(f_level0[2].access_internal, "edit")
        self.assertEqual(f_level0[2].access_via_link, "none")

        self.assertFalse(f_level1[0].access_ids)
        self.assertEqual(f_level1[0].access_internal, "edit")
        self.assertEqual(f_level1[0].access_via_link, "view")

        self.assertFalse(f_level1[3].access_ids)
        self.assertEqual(f_level1[3].access_internal, "edit")
        self.assertEqual(f_level1[3].access_via_link, "none")

        self.assertEqual(
            f_level2[7].access_ids.mapped("partner_id"),
            (users_internals | users_admins).partner_id,
        )
        self.assertEqual(f_level2[7].access_internal, "none")
        self.assertEqual(f_level2[7].access_via_link, "view")
        self.assertEqual(f_level2[7].is_access_via_link_hidden, True)

        # check the propagation of the access of the folder on the documents
        self.assertEqual(
            documents[0].access_ids.mapped("partner_id"),
            users_admins.partner_id,
        )
        self.assertEqual(documents[0].access_ids.mapped("role"), ["edit"] * 3)

        # "other_group" gained write access, "system" gained read access
        for document in (documents[10], documents[10].folder_id):
            self.assertEqual(
                document.access_ids.mapped("partner_id"),
                (users_admins | users_internals).partner_id,
            )
            access = document.access_ids
            other_group_access = access.filtered(lambda a: a.partner_id in users_internals.partner_id)
            system_group_access = access.filtered(lambda a: a.partner_id in users_admins.partner_id)
            self.assertEqual(other_group_access.mapped("role"), ["edit", "edit"])
            self.assertEqual(system_group_access.mapped("role"), ["view", "view", "view"])

        # Check user_specific
        doc_1, doc_2, doc_3 = documents[7], documents[8], documents[9]
        self.assertEqual(doc_1.access_internal, "none")
        self.assertEqual(doc_1.access_via_link, "view")
        self.assertEqual(doc_2.access_internal, "none")
        self.assertEqual(doc_2.access_via_link, "view")
        self.assertEqual(doc_3.access_internal, "none")
        self.assertEqual(doc_3.access_via_link, "view")

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
        self.assertEqual(doc_1.partner_id, users_internals[1].partner_id)
        self.assertEqual(doc_2.owner_id, self.env.ref("base.user_root"))
        self.assertEqual(doc_2.partner_id, users_internals[1].partner_id, "The partner was set, do not change it")
        self.assertEqual(doc_3.owner_id, users_internals[0])
        self.assertFalse(doc_3.partner_id, "The owner is not reset, do not change the contact")

        # Check that the folders are not accessible for all users if they have a write group
        # (eg, the payslip folders won't be visible anymore, only HR user can write inside,
        # but payslips inside of it will still be accessible in "Shared With Me")
        self.assertEqual(f_level2[4].access_internal, "view")
        self.assertFalse(f_level2[4].access_ids)
        self.assertEqual(f_level2[5].access_internal, "view")
        self.assertFalse(f_level2[5].access_ids)
        self.assertEqual(f_level2[8].access_internal, "none")
        self.assertEqual(f_level2[8].access_ids.mapped("role"), ["edit", "edit", "edit"])

        # Global checks
        self.assertEqual(
            documents.mapped("access_internal"),
            ["none", "edit", "none", "edit", "edit", "edit", "edit"] + ["none"] * 4,
        )
        self.assertEqual(
            documents.mapped("access_via_link"),
            ["view", "view", "none"] + ["view"] * 8,
        )
        self.assertEqual(
            documents.mapped("is_access_via_link_hidden"),
            [True] + [False] * 6 + [True, True, True, False],
        )

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

        self.assertFalse(f_level1[0].company_id)
        self.assertFalse(f_level1[1].company_id)
        self.assertEqual(f_level1[2].company_id, companies[0])

        self.assertEqual(f_level2[0].company_id, companies[1])
        self.assertFalse(f_level2[1].company_id)
        self.assertFalse(f_level2[2].company_id)
        self.assertFalse(f_level2[3].company_id)

        self.assertEqual(documents[0].company_id, companies[0])
        self.assertFalse(documents[1].company_id)  # f_level0[2] has no company
        # inherit from f_level2[0]
        self.assertEqual(documents[5].company_id, companies[1])

        ###################
        # WORK FLOW RULES #
        ###################
        activity_type_todo = self.env.ref("mail.mail_activity_data_todo")
        activity_type_call = self.env.ref("mail.mail_activity_data_call")
        internal_user = self.env.ref("base.group_user")
        doc_a_base = documents[0]

        def get_server_action(name):
            act_server = self.env["ir.actions.server"].search([("name", "=", name)])
            self.assertTrue(act_server)
            self.assertEqual(act_server.groups_id, internal_user)
            return act_server

        def get_embedded_action(act_server):
            embedded_action = self.env["ir.embedded.actions"].search(
                [
                    ("action_id", "=", act_server.id),
                    ("parent_action_id", "=", self.env.ref("documents.document_action").id),
                    ("name", "=", act_server.name),
                    ("parent_res_model", "=", "documents.document"),
                    ("parent_res_id", "=", f_level0[0].id),
                ]
            )
            self.assertTrue(embedded_action)
            self.assertEqual(embedded_action.groups_ids, internal_user)
            return embedded_action

        def check_activity_common(activity):
            self.assertEqual(activity.summary, "Test workflow rule activity summary")
            self.assertEqual(activity.note, "<p>Test workflow rule activity note</p>")

        def get_doc_a_copy():
            doc_a = doc_a_base.copy()
            doc_a.res_id = doc_a.id  # copy doesn't set correctly res_id
            doc_a.activity_schedule("mail.mail_activity_data_call")
            self.assertEqual(doc_a.activity_ids.activity_type_id, activity_type_call)
            return doc_a.with_context(active_model="documents.document", active_id=doc_a.id)

        def check_base(activity):
            check_activity_common(activity)
            self.assertEqual(activity.activity_type_id, activity_type_todo)
            self.assertEqual(activity.date_deadline, date.today() + relativedelta(months=2))
            self.assertEqual(activity.user_id, doc_a.owner_id)
            self.assertEqual(doc_a.folder_id, f_level0[1])
            self.assertEqual(doc_a.res_id, doc_a.id)
            self.assertEqual(doc_a.res_model, "documents.document")

        # Check workflow rule conversion that only depends on documents (and not submodules)
        with freeze_time("1900-01-04"):
            act_server = get_server_action("MiGraTion18-Base")
            embedded_action = get_embedded_action(act_server)
            self.assertEqual(
                set(act_server.child_ids.mapped("name")),
                {
                    "Mark activities as completed",
                    "Remove Tag Tag 2",
                    "Remove Tag Tag 3",
                    "Add Tag Tag 1",
                    "Create Activity To-Do",
                    "MiGraTion18-Base_custom_code",
                },
            )
            doc_a = get_doc_a_copy()
            action = doc_a.action_execute_embedded_action(embedded_action.id)
            self.assertFalse(action)
            self.assertEqual(set(doc_a.tag_ids.mapped("name")), {"Tag 1", "Tag A"})
            check_base(doc_a.activity_ids)

            act_server = get_server_action("MiGraTion18-LinkToRecord")
            embedded_action = get_embedded_action(act_server)
            doc_a = get_doc_a_copy()
            self.assertEqual(
                set(act_server.child_ids.mapped("name")),
                {
                    "Mark activities as completed",
                    "Remove Tag Tag 1",
                    "Create Activity Call",
                    "MiGraTion18-LinkToRecord_custom_code",
                    "ir_actions_server_link_to",
                },
            )
            action = doc_a.action_execute_embedded_action(embedded_action.id)
            self.assertEqual(
                action,
                {
                    "name": "Choose a record to link",
                    "type": "ir.actions.act_window",
                    "res_model": "documents.link_to_record_wizard",
                    "view_mode": "form",
                    "target": "new",
                    "views": [(False, "form")],
                    "context": {
                        "default_document_ids": doc_a.ids,
                        "default_resource_ref": False,
                        "default_is_readonly_model": False,
                        "default_model_ref": False,
                    },
                },
            )
            self.assertEqual(set(doc_a.tag_ids.mapped("name")), {"Tag A", "Tag 2", "Tag 3"})
            activity = doc_a.activity_ids
            check_activity_common(activity)
            self.assertEqual(activity.activity_type_id, activity_type_call)
            self.assertEqual(activity.date_deadline, date.today() + relativedelta(months=2))
            self.assertEqual(activity.user_id, users_internals[0])
            self.assertEqual(doc_a.folder_id, f_level0[1])
            self.assertEqual(doc_a.res_id, doc_a.id)
            self.assertEqual(doc_a.res_model, "documents.document")

            act_server = get_server_action("MiGraTion18-LinkToContactRecord")
            embedded_action = get_embedded_action(act_server)
            doc_a = get_doc_a_copy()
            self.assertEqual(
                set(act_server.child_ids.mapped("name")),
                {
                    "Add Tag Tag 1",
                    "Create Activity To-Do",
                    "MiGraTion18-LinkToContactRecord_custom_code",
                    "ir_actions_server_link_to_res_partner",
                },
            )
            action = doc_a.action_execute_embedded_action(embedded_action.id)
            first_valid_partner_id = self.env["res.partner"].search([], limit=1).id
            self.assertEqual(
                action,
                {
                    "name": "Choose a record to link",
                    "type": "ir.actions.act_window",
                    "res_model": "documents.link_to_record_wizard",
                    "view_mode": "form",
                    "target": "new",
                    "views": [(False, "form")],
                    "context": {
                        "default_document_ids": doc_a.ids,
                        "default_resource_ref": f"res.partner,{first_valid_partner_id}",
                        "default_is_readonly_model": True,
                        "default_model_ref": False,
                        "default_model_id": self.env.ref("base.model_res_partner").id,
                    },
                },
            )
            self.assertEqual(set(doc_a.tag_ids.mapped("name")), {"Tag A", "Tag 1", "Tag 2", "Tag 3"})
            self.assertEqual(doc_a.activity_ids.activity_type_id, activity_type_call | activity_type_todo)
            activity_by_type = {act.activity_type_id: act for act in doc_a.activity_ids}
            activity = activity_by_type[activity_type_todo]
            check_activity_common(activity)
            self.assertEqual(activity.date_deadline, date.today() + relativedelta(days=3))
            self.assertEqual(activity.user_id, users_internals[1])
            self.assertEqual(doc_a.folder_id, f_level0[2])
            self.assertEqual(doc_a.res_id, doc_a.id)
            self.assertEqual(doc_a.res_model, "documents.document")

            # Check workflow rules of submodules that create specific records.
            if util.module_installed(self.env.cr, "documents_account") and init["journal_ids"]:
                journal_id = init["journal_ids"][0]
                companies = [(False, False), (self.env.company.id, self.env.company.name)]
                for move_type, (company_id, company_name) in itertools.product(ACCOUNT_MOVE_TYPES, companies):
                    act_server = get_server_action(
                        f"MiGraTion18-Create-account.move-{move_type}{f' ({company_name})' if company_name else ''}"
                    )
                    embedded_action = get_embedded_action(act_server)
                    doc_a = get_doc_a_copy()
                    with patch.object(
                        type(self.env["documents.document"]), "account_create_account_move", autospec=True
                    ) as mock_create:
                        doc_a.action_execute_embedded_action(embedded_action.id)
                    mock_create.assert_called_once_with(doc_a, move_type, *([journal_id] if company_id else []))
                    check_base(doc_a.activity_ids)
                for company_id, company_name in companies:
                    act_server = get_server_action(
                        f"MiGraTion18-Create-account.bank.statement{f' ({company_name})' if company_name else ''}"
                    )
                    embedded_action = get_embedded_action(act_server)
                    doc_a = get_doc_a_copy()
                    with patch.object(
                        type(self.env["documents.document"]), "account_create_account_bank_statement", autospec=True
                    ) as mock_create:
                        doc_a.action_execute_embedded_action(embedded_action.id)
                    mock_create.assert_called_once_with(doc_a, *((journal_id,) if company_id else ()))
                check_base(doc_a.activity_ids)

            for module, create_infos in (
                ("documents_hr_expense", [("hr.expense", "document_hr_expense_create_hr_expense", [])]),
                ("documents_hr_recruitment", [("hr.applicant", "document_hr_recruitment_create_hr_candidate", [])]),
                ("documents_product", [("product.template", "create_product_template", [])]),
                ("documents_project", [("project.task", "action_create_project_task", [])]),
                (
                    "documents_sign",
                    [
                        ("sign.template.new", "document_sign_create_sign_template_x", ["sign.template.new"]),
                        ("sign.template.direct", "document_sign_create_sign_template_x", ["sign.template.direct"]),
                    ],
                ),
            ):
                if module in installed_modules:
                    for create_model, method_name, parameters in create_infos:
                        doc_a = get_doc_a_copy()
                        act_server = get_server_action(f"MiGraTion18-Create-{create_model}")
                        create_model_act_server_name = f"ir_actions_server_{method_name}"
                        if parameters:
                            create_model_act_server_name += "_" + ("_".join(parameters))
                        self.assertIn(create_model_act_server_name, set(act_server.child_ids.mapped("name")))
                        with patch.object(
                            type(self.env["documents.document"]), method_name, autospec=True
                        ) as mock_create:
                            if create_model == "sign.template.direct":
                                # Action related to sign.template.direct can only be executed on one document -> no embedded action
                                self.assertFalse(
                                    self.env["ir.embedded.actions"].search([("action_id", "=", act_server.id)])
                                )
                                act_server.with_context(active_model="documents.document", active_id=doc_a.id).run()
                            else:
                                embedded_action = get_embedded_action(act_server)
                                doc_a.action_execute_embedded_action(embedded_action.id)
                        mock_create.assert_called_once_with(*[doc_a, *parameters])
                        check_base(doc_a.activity_ids)

            # Check that no embedded actions are created for workflow rule with criteria (as we can ensure those criteria)
            for criteria in (
                "domain",
                "criteria_partner_id",
                "criteria_owner_id",
                "required_tag_ids",
                "excluded_tag_ids",
            ):
                act_server = self.env["ir.actions.server"].search([("name", "=", f"MiGraTion18-Criterion-{criteria}")])
                self.assertTrue(act_server)
                self.assertFalse(self.env["ir.embedded.actions"].search([("action_id", "=", act_server.id)]))
