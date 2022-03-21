# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.4")
class TestMigrateAncestorId(UpgradeCase):
    def prepare(self):
        def create_task(**values):
            return self.env["project.task"].with_context(pad_no_create=True).create(values)

        project = (
            self.env["project.project"]
            .with_context(pad_no_create=True)
            .create(
                {
                    "name": "Project 1",
                }
            )
        )
        parent_task = create_task(name="Parent Task", project_id=project.id)
        task = create_task(name="Task", parent_id=parent_task.id)
        child_task = create_task(name="Child Task", parent_id=task.id)

        child_task2 = create_task(name="Child Task2", project_id=project.id)
        task2 = create_task(name="Task2", project_id=project.id)
        child_task2.parent_id = task2.id
        parent_task2 = create_task(name="Parent Task2", project_id=project.id)
        task2.parent_id = parent_task2.id
        return [
            {"id": parent_task.id, "children": {"id": task.id, "children": {"id": child_task.id}}},
            {"id": parent_task2.id, "children": {"id": task2.id, "children": {"id": child_task2.id}}},
        ]

    def check(self, init):
        tree1_data = init[0]
        tree2_data = init[1]
        Task = self.env["project.task"]
        parent_task = Task.browse(tree1_data["id"])
        task = Task.browse(tree1_data["children"]["id"])
        child_task = Task.browse(tree1_data["children"]["children"]["id"])
        child_task2 = Task.browse(tree2_data["children"]["children"]["id"])
        task2 = Task.browse(tree2_data["children"]["id"])
        parent_task2 = Task.browse(tree2_data["id"])

        self.assertFalse(parent_task.ancestor_id, "Ancestor Task should be False For Root Task.")
        self.assertEqual(task.ancestor_id, task.parent_id, "Ancestor Task should be Parent Task For Level 1 Tree.")
        self.assertEqual(
            child_task.ancestor_id,
            task.parent_id,
            "Ancestor Task should be Parent Task of Parent Task For Level 2 Tree.",
        )

        self.assertFalse(parent_task2.ancestor_id, "Ancestor Task should be False For Root Task.")
        self.assertEqual(task2.ancestor_id, task2.parent_id, "Ancestor Task should be Parent Task For Level 1 Tree.")
        self.assertEqual(
            child_task2.ancestor_id,
            task2.parent_id,
            "Ancestor Task should be Parent Task of Parent Task For Level 2 Tree.",
        )
