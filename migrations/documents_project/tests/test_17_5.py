import contextlib

with contextlib.suppress(ImportError):
    from odoo import Command

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestShareMigration(UpgradeCase):
    def prepare(self):
        if not util.version_gte("saas~17.4"):
            return None

        Folder = self.env["documents.folder"]
        Document = self.env["documents.document"]
        Share = self.env["documents.share"]

        folder_projects_main = Folder.create({"name": "Projects (Main)"})
        folder_project_a, folder_project_b, folder_project_d, folder_project_e = Folder.create(
            [
                {"name": "Project A", "parent_folder_id": False},
                {"name": "Project B", "parent_folder_id": folder_projects_main.id},
                {"name": "Project D", "parent_folder_id": folder_projects_main.id},
                {"name": "Project E", "parent_folder_id": folder_projects_main.id},
            ]
        )
        folder_project_c = Folder.create(
            [
                {"name": "Project C", "parent_folder_id": folder_project_b.id},
            ]
        )
        folders_projects = folder_project_a | folder_project_b | folder_project_c | folder_project_d | folder_project_e
        _, _, subfolder_c, *_ = Folder.create(
            [{"name": f"Subfolder {folder.name}", "parent_folder_id": folder.id} for folder in folders_projects]
        )
        projects = project_a, project_b, project_c, project_d, project_e = self.env["project.project"].create(
            [
                {
                    "name": f"Project {chr(65+idx)}",
                    "documents_folder_id": folders_projects[idx].id,
                    "privacy_visibility": ["employees", "followers", "portal", "followers", "portal"][idx],
                    "use_documents": True,
                }
                for idx in range(5)
            ]
        )

        tasks = task_a_a, task_a_b, task_b_a, task_b_b, task_c_a, task_c_b, task_d_a, task_d_b = self.env[
            "project.task"
        ].create(
            [
                {"name": f"Task {chr(65 + t_idx)} - {project.name}", "project_id": project.id}
                for project in projects[:4]  # not needed for E
                for t_idx in range(2)
            ]
        )
        documents_projects = [Document] * 4
        for idx, (project, task_a, task_b) in enumerate(
            [
                (project_a, task_a_a, task_a_b),
                (project_b, task_b_a, task_b_b),
                (project_c, task_c_a, task_c_b),
                (project_d, task_d_a, task_d_b),
            ]
        ):
            p_chr = chr(65 + idx)
            project_folder = project.documents_folder_id
            project_subfolder = project_folder.children_folder_ids.filtered(lambda d: d.name.startswith("Subfolder"))
            self.assertEqual(len(project_subfolder), 1)
            link_project_values = {"res_model": "project.project", "res_id": project.id}
            link_task_a_values = {"res_model": "project.task", "res_id": task_a.id}
            link_task_b_values = {"res_model": "project.task", "res_id": task_b.id}
            documents_projects[idx] = Document.create(
                [
                    {"name": f"{p_chr}1", "folder_id": (project_folder if idx < 2 else project_subfolder).id},
                    {"name": f"P{p_chr}1", "folder_id": project_folder.id} | link_project_values,
                    {"name": f"P{p_chr}TA1", "folder_id": project_folder.id} | link_task_a_values,
                    {"name": f"P{p_chr}TA2", "folder_id": project_subfolder.id} | link_task_a_values,
                    {"name": f"P{p_chr}TB1", "folder_id": project_folder.id} | link_task_b_values,
                    {"name": f"P{p_chr}TB2", "folder_id": project_subfolder.id} | link_task_b_values,
                ]
            )

        documents = documents_projects[0] | documents_projects[1] | documents_projects[2] | documents_projects[3]

        Share.create(
            [
                {
                    "name": "Share Folder Project A",
                    "folder_id": folder_project_a.id,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", folder_project_a.id]],
                },
                {
                    "name": "Share Folder Project D",
                    "folder_id": folder_project_d.id,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", folder_project_d.id]],
                },
                {
                    "name": "Share Folder Project E",
                    "folder_id": folder_project_e.id,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", folder_project_e.id]],
                },
                {
                    "name": "Share Document B1",
                    "folder_id": folder_project_b.id,
                    "type": "ids",
                    "document_ids": [Command.link(documents_projects[1][0].id)],
                },
                {
                    "name": "Share Document PB1",
                    "folder_id": folder_project_b.id,
                    "type": "ids",
                    "document_ids": [Command.link(documents_projects[1][1].id)],
                },
                {
                    "name": "Share Document PBTA1",
                    "folder_id": folder_project_b.id,
                    "type": "ids",
                    "document_ids": [Command.link(documents_projects[1][2].id)],
                },
                {
                    "name": "Share Document PC1",
                    "folder_id": folder_project_c.id,
                    "type": "ids",
                    "document_ids": [Command.link(documents_projects[2][1].id)],
                },
                {
                    "name": "Share Document PCTA1",
                    "folder_id": folder_project_c.id,
                    "type": "ids",
                    "document_ids": [Command.link(documents_projects[2][2].id)],
                },
                {
                    "name": "Share SubFolder Project C",
                    "folder_id": subfolder_c.id,
                    "type": "domain",
                    "domain": [["folder_id", "child_of", subfolder_c.id]],
                },
            ]
        )

        user_internal_1, user_internal_2 = users = self.env["res.users"].create(
            [
                {"name": "User Internal 1", "login": "user_internal_1"},
                {"name": "User Internal 2", "login": "user_internal_2"},
            ]
        )

        portal_1, portal_2 = portal_partners = self.env["res.partner"].create(
            [
                {"name": "Partner 1"},
                {"name": "Partner 2"},
            ]
        )

        # Create followers (will be added as documents members on shared documents depending on privacy visibility)
        (project_a | project_b | project_c | project_d | project_e).message_subscribe(partner_ids=portal_1.ids)
        (project_b | project_c | project_d | project_e).message_subscribe(partner_ids=user_internal_1.partner_id.ids)
        task_b_a.message_subscribe(partner_ids=portal_2.ids)
        task_b_b.message_subscribe(partner_ids=user_internal_2.ids)
        (task_c_a | task_c_b).message_subscribe(partner_ids=portal_2.ids)

        return {
            "project_ids": projects.ids,
            "task_ids": tasks.ids,
            "document_ids": documents.ids,
            "user_ids": users.ids,
            "portal_partner_ids": portal_partners.ids,
        }

    def check(self, init):
        if not init:
            return

        projects = self.env["project.project"].browse(init["project_ids"])
        users = self.env["res.users"].browse(init["user_ids"])
        portal_partners = self.env["res.partner"].browse(init["portal_partner_ids"])

        folder_project_a, folder_project_b, folder_project_c, folder_project_d, folder_project_e = (
            projects.documents_folder_id
        )
        self.assertEqual(folder_project_a.access_via_link, "view", "The project folder was shared")
        self.assertEqual(folder_project_a.access_internal, "edit", 'project privacy visibility was "employee"')
        documents_project_a = self.env["documents.document"].search([("id", "child_of", folder_project_a.id)])
        self.assertEqual(len(documents_project_a), 8)

        documents_project_c = self.env["documents.document"].search([("id", "child_of", folder_project_c.id)])
        self.assertEqual(len(documents_project_c), 8)

        documents_project_b = self.env["documents.document"].search(
            [("id", "child_of", folder_project_b.id), "!", ("id", "child_of", folder_project_c.id)]
        )
        self.assertEqual(len(documents_project_b), 8)

        self.assertEqual(set(documents_project_a.mapped("access_via_link")), {"view"})
        self.assertEqual(set(documents_project_a.mapped("is_access_via_link_hidden")), {False})
        self.assertEqual(
            documents_project_a.access_ids.partner_id,
            self.env["res.partner"],
            'Followers shouldn\'t get access to documents with "employee" project privacy visibility',
        )

        self.assertEqual(folder_project_b.access_via_link, "none", "The project folder was not shared")
        self.assertFalse(folder_project_b.is_access_via_link_hidden, "Default as the project folder was not shared")
        self.assertEqual(folder_project_b.access_internal, "none", 'project privacy visibility was "followers"')
        self.assertFalse(folder_project_b.access_ids.partner_id, "Project folder was not shared")

        self.assertEqual(folder_project_c.access_via_link, "none", "The project folder was not shared")
        self.assertFalse(folder_project_c.is_access_via_link_hidden, "Default as the project folder was not shared")
        self.assertEqual(folder_project_c.access_internal, "edit", 'project privacy visibility was "portal"')
        self.assertFalse(folder_project_c.access_ids.partner_id, "Project folder was not shared")

        self.assertEqual(folder_project_d.access_via_link, "view", "Shared for internal users followers")
        self.assertTrue(folder_project_d.is_access_via_link_hidden, "Should not be discoverable from Projects folder")
        self.assertEqual(folder_project_d.access_internal, "none", 'project privacy visibility was "followers"')
        self.assertEqual(folder_project_d.access_ids.partner_id, users[0].partner_id, "Only internal user follower")

        self.assertEqual(folder_project_e.access_via_link, "view", "Shared for portal users followers")
        self.assertEqual(folder_project_e.access_internal, "edit", 'project privacy visibility was "portal"')
        self.assertEqual(folder_project_e.access_ids.partner_id, portal_partners[0], "Only portal follower")

        documents = self.env["documents.document"].browse(init["document_ids"])
        documents_project_a = documents_project_a & documents_project_a.browse(documents[:6].ids)
        self.assertEqual(len(documents_project_a), 6)
        self.assertFalse(documents_project_a.access_ids)

        documents_project_b = documents_project_b & documents_project_b.browse(documents[6:12].ids)
        project_b_access = set(
            documents_project_b.access_ids.mapped(lambda d: f"{d.document_id.name} - {d.partner_id.name}")
        )
        self.assertEqual(
            project_b_access,
            {"B1 - User Internal 1", "PB1 - User Internal 1", "PBTA1 - User Internal 1"},
            "Access given to project-following internal user",
        )
        shared = documents_project_b.access_ids.document_id
        self.assertEqual(set(shared.mapped("access_via_link")), {"view"})
        not_shared = documents_project_b - shared
        self.assertEqual(set(not_shared.mapped("access_via_link")), {"none"})

        task_b_a, task_b_b = init["task_ids"][2:4]
        self.assertEqual(
            set(documents_project_b.mapped(lambda d: (d.name, d.res_model, d.res_id))),
            {
                ("B1", "project.project", projects[1].id),
                ("PB1", "project.project", projects[1].id),
                ("PBTA1", "project.task", task_b_a),
                ("PBTA2", "project.task", task_b_a),
                ("PBTB1", "project.task", task_b_b),
                ("PBTB2", "project.task", task_b_b),
            },
        )

        documents_project_c = documents_project_c & documents_project_c.browse(documents[12:18].ids)
        project_c_access = set(
            documents_project_c.access_ids.mapped(lambda d: f"{d.document_id.name} - {d.partner_id.name}")
        )
        self.assertEqual(
            project_c_access,
            {
                "C1 - Partner 1",  # Via share of document
                "PC1 - Partner 1",  # Via share of document
                "PCTA1 - Partner 1",  # Via share of document
                "PCTA1 - Partner 2",  # idem
                "PCTA2 - Partner 1",  # Via share of project subfolder
                "PCTA2 - Partner 2",  # idem
                "PCTB2 - Partner 1",  # Via share of project subfolder
                "PCTB2 - Partner 2",  # idem
            },
            "Access given to project- and task-following portal followers ",
        )
        shared = documents_project_c.access_ids.document_id
        self.assertEqual(set(shared.mapped("access_via_link")), {"view"})
        not_shared = documents_project_c - shared
        self.assertEqual(set(not_shared.mapped("access_via_link")), {"none"})

        task_c_a, task_c_b = init["task_ids"][4:6]
        self.assertEqual(
            set(documents_project_c.mapped(lambda d: (d.name, d.res_model, d.res_id))),
            {
                ("C1", "project.project", projects[2].id),
                ("PC1", "project.project", projects[2].id),
                ("PCTA1", "project.task", task_c_a),
                ("PCTA2", "project.task", task_c_a),
                ("PCTB1", "project.task", task_c_b),
                ("PCTB2", "project.task", task_c_b),
            },
        )
