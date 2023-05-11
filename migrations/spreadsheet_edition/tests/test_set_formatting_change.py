# -*- coding: utf-8 -*-

import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("16.3")
class TestSpreadsheetChangeSetFormattingCmd(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None

        commands = [
            {"type": "TYPE_UNKNOWN_COMMAND_01", "other": "stuff"},
            {
                "type": "SET_FORMATTING",
                "style": {"textColor": "#123456"},
                "target": [{"top": 0, "left": 0, "bottom": 0, "right": 0}],
                "sheetId": "Sheet1",
            },
            {
                "type": "SET_FORMATTING",
                "style": {"fillColor": "#123456"},
                "target": [{"top": 1, "left": 0, "bottom": 1, "right": 0}],
                "sheetId": "Sheet1",
            },
            {"type": "TYPE_UNKNOWN_COMMAND_02", "other": "stuff"},
            {
                "type": "SET_FORMATTING",
                "style": {"bold": True},
                "target": [{"top": 2, "left": 0, "bottom": 2, "right": 0}],
                "sheetId": "Sheet1",
            },
            {"type": "TYPE_UNKNOWN_COMMAND_03", "other": "stuff"},
            {
                "type": "SET_FORMATTING",
                "style": {"textColor": "#123456"},
                "target": [{"top": 0, "left": 1, "bottom": 0, "right": 1}],
                "border": "external",
                "sheetId": "Sheet1",
            },
            {"type": "TYPE_UNKNOWN_COMMAND_04", "other": "stuff"},
            {
                "type": "SET_FORMATTING",
                "style": {"fillColor": "#123456"},
                "target": [{"top": 1, "left": 1, "bottom": 1, "right": 1}],
                "border": "left",
                "sheetId": "Sheet1",
            },
            {"type": "TYPE_UNKNOWN_COMMAND_05", "other": "stuff"},
            {
                "type": "SET_FORMATTING",
                "style": {"bold": True},
                "target": [{"top": 2, "left": 1, "bottom": 2, "right": 1}],
                "border": "bottom",
                "sheetId": "Sheet1",
            },
            {"type": "TYPE_UNKNOWN_COMMAND_06", "other": "stuff"},
            {
                "type": "SET_FORMATTING",
                "target": [{"top": 0, "left": 2, "bottom": 3, "right": 3}],
                "border": "all",
                "sheetId": "Sheet1",
            },
            {"type": "TYPE_UNKNOWN_COMMAND_07", "other": "stuff"},
        ]

        revision_commands = {
            "type": "REMOTE_REVISION",
            "commands": commands,
        }

        revisions_insert = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_commands),
                    "parent_revision_id": "A",
                    "revision_id": "B",
                },
            ]
        )

        return revisions_insert.id

    def check(self, revision_id):
        if not revision_id:
            return
        revision = self.env["spreadsheet.revision"].browse(revision_id)

        commands = json.loads(revision.commands)["commands"]
        self.assertEqual(
            commands,
            [
                {"type": "TYPE_UNKNOWN_COMMAND_01", "other": "stuff"},
                {
                    "type": "SET_FORMATTING",
                    "style": {"textColor": "#123456"},
                    "target": [{"top": 0, "left": 0, "bottom": 0, "right": 0}],
                    "sheetId": "Sheet1",
                },
                {
                    "type": "SET_FORMATTING",
                    "style": {"fillColor": "#123456"},
                    "target": [{"top": 1, "left": 0, "bottom": 1, "right": 0}],
                    "sheetId": "Sheet1",
                },
                {"type": "TYPE_UNKNOWN_COMMAND_02", "other": "stuff"},
                {
                    "type": "SET_FORMATTING",
                    "style": {"bold": True},
                    "target": [{"top": 2, "left": 0, "bottom": 2, "right": 0}],
                    "sheetId": "Sheet1",
                },
                {"type": "TYPE_UNKNOWN_COMMAND_03", "other": "stuff"},
                {
                    "type": "SET_ZONE_BORDERS",
                    "target": [{"top": 0, "left": 1, "bottom": 0, "right": 1}],
                    "border": {"position": "external"},
                    "sheetId": "Sheet1",
                },
                {
                    "type": "SET_FORMATTING",
                    "style": {"textColor": "#123456"},
                    "target": [{"top": 0, "left": 1, "bottom": 0, "right": 1}],
                    "sheetId": "Sheet1",
                },
                {"type": "TYPE_UNKNOWN_COMMAND_04", "other": "stuff"},
                {
                    "type": "SET_ZONE_BORDERS",
                    "target": [{"top": 1, "left": 1, "bottom": 1, "right": 1}],
                    "border": {"position": "left"},
                    "sheetId": "Sheet1",
                },
                {
                    "type": "SET_FORMATTING",
                    "style": {"fillColor": "#123456"},
                    "target": [{"top": 1, "left": 1, "bottom": 1, "right": 1}],
                    "sheetId": "Sheet1",
                },
                {"type": "TYPE_UNKNOWN_COMMAND_05", "other": "stuff"},
                {
                    "type": "SET_ZONE_BORDERS",
                    "target": [{"top": 2, "left": 1, "bottom": 2, "right": 1}],
                    "border": {"position": "bottom"},
                    "sheetId": "Sheet1",
                },
                {
                    "type": "SET_FORMATTING",
                    "style": {"bold": True},
                    "target": [{"top": 2, "left": 1, "bottom": 2, "right": 1}],
                    "sheetId": "Sheet1",
                },
                {"type": "TYPE_UNKNOWN_COMMAND_06", "other": "stuff"},
                {
                    "type": "SET_ZONE_BORDERS",
                    "target": [{"top": 0, "left": 2, "bottom": 3, "right": 3}],
                    "border": {"position": "all"},
                    "sheetId": "Sheet1",
                },
                {"type": "TYPE_UNKNOWN_COMMAND_07", "other": "stuff"},
            ],
        )
