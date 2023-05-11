# -*- coding: utf-8 -*-

import json
import logging

from odoo.upgrade import util

_logger = logging.getLogger("odoo.upgrade.spreadsheet_edition.saas-16.3." + __name__)


def migrate(cr, version):
    cr.execute(
        """
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%SET_FORMATTING%'
           AND commands LIKE '%border%'
        """
    )

    for revision_id, data in util.log_progress(cr.fetchall(), _logger, qualifier="spreadsheet revisions"):
        json_data = json.loads(data)
        formatting_commands = json_data.get("commands", [])
        if not formatting_commands:
            continue
        new_commands = []
        changed = False

        for formatting_command in formatting_commands:
            if formatting_command.get("type") == "SET_FORMATTING" and "border" in formatting_command:
                changed = True
                if "style" in formatting_command or "format" in formatting_command:
                    new_commands.append(
                        {
                            "type": "SET_ZONE_BORDERS",
                            "sheetId": formatting_command["sheetId"],
                            "target": formatting_command["target"],
                            "border": {
                                "position": formatting_command["border"],
                            },
                        }
                    )
                    del formatting_command["border"]
                else:
                    formatting_command["type"] = "SET_ZONE_BORDERS"
                    formatting_command["border"] = {"position": formatting_command["border"]}
            new_commands.append(formatting_command)

        if not changed:
            continue

        json_data["commands"] = new_commands
        cr.execute(
            """
            UPDATE spreadsheet_revision
               SET commands=%s
             WHERE id=%s
            """,
            [json.dumps(json_data), revision_id],
        )
