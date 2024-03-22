import json
import logging

from odoo.upgrade.spreadsheet.tokenizer import tokenize

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Starting migration to remove ODOO.PIVOT.POSITION")

    cr.execute(
        """
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE res_model = 'spreadsheet.template'
            AND commands LIKE '%UPDATE_CELL%'
            AND commands LIKE '%ODOO.PIVOT.POSITION%'
        """
    )

    def _pivot_position_to_pivot(content):
        if content and content.startswith("=") and "ODOO.PIVOT.POSITION" in content:
            tokens = tokenize(content)
            # given that odoo.pivot.position is automatically set, we know that:
            # 1) it is always on the form of ODOO.PIVOT.POSITION(1, ...)
            # 2) it is always preceded by a dimension of a pivot or header, inside another pivot formula
            # 3) there is only one odoo.pivot.position per cell
            # 4) odoo.pivot.position can only exist after the 3rd token and needs at least 7 tokens to be valid
            for i in range(2, len(tokens) - 7):
                token = tokens[i]
                if token == ("SYMBOL", "ODOO.PIVOT.POSITION"):
                    order = tokens[i + 6]
                    tokens[i - 2] = tokens[i - 2][0], '"#' + tokens[i - 2][1][1:]  # "dimension" becomes "#dimension"
                    del tokens[i : i + 7]  # remove "ODOO.PIVOT.POSITION", "(", "1", ",", "dimension", ", ", order
                    # tokens[i-1] is the comma before odoo.pivot.position
                    tokens[i] = order
                    return "".join(token[1] for token in tokens)
        return None

    _logger.info("Processing %s revisions with ODOO.PIVOT.POSITION", cr.rowcount)
    for revision_id, payload in cr.fetchall():
        data = json.loads(payload)
        commands = data.get("commands", [])
        if not commands:
            continue
        pivot_update_cell = [cmd for cmd in commands if (cmd.get("type") == "UPDATE_CELL" and cmd.get("content"))]
        _logger.info("Processing %s cells with ODOO.PIVOT.POSITION", len(pivot_update_cell))
        for cmd in pivot_update_cell:
            cmd["content"] = _pivot_position_to_pivot(cmd["content"]) or cmd["content"]
        if pivot_update_cell:
            cr.execute(
                """
                UPDATE spreadsheet_revision
                   SET commands=%s
                 WHERE id=%s
                """,
                [json.dumps(data), revision_id],
            )
