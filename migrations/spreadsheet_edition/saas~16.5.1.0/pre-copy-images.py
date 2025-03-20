import uuid

from odoo.upgrade import util
from odoo.upgrade.util import json


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id, commands, res_model, res_id
          FROM spreadsheet_revision
         WHERE commands LIKE '%CREATE_IMAGE%'
        """
    )

    for revision_id, stringified_data, res_model, res_id in cr.fetchall():
        data = json.loads(stringified_data)
        commands = data.get("commands", [])
        if not commands:
            continue

        changed = False
        for command in commands:
            if command["type"] == "CREATE_IMAGE" and fix_image_attachment(cr, res_model, res_id, command):
                changed = True
        if not changed:
            continue

        data["commands"] = commands
        cr.execute(
            """
            UPDATE spreadsheet_revision
               SET commands=%s
             WHERE id=%s
            """,
            [json.dumps(data), revision_id],
        )


def fix_image_attachment(cr, res_model, res_id, command):
    """
    Some spreadsheets have images that are linked to an attachment that is linked to an other spreadsheet
    record. This detects such a situation and to copies the attachment and replace the image path
    with the new attachment path."""
    path = command["definition"]["path"]
    if path.startswith("/web/image/"):
        # path is /web/image/<attachment_id>?...
        path = path.split("?")[0]
        if not path.split("/")[3].isdigit():
            return False
        attachment_id = int(path.split("/")[3])
        cr.execute(
            """
            SELECT res_model, res_id
            FROM ir_attachment
            WHERE id=%s
            """,
            [attachment_id],
        )
        if not cr.rowcount:
            return False
        attachment_res_model, attachment_res_id = cr.fetchone()
        if attachment_res_model != res_model or attachment_res_id != res_id:
            new_attachment_id, access_token = copy_attachment(cr, attachment_id, res_model, res_id)

            path = f"/web/image/{new_attachment_id}"
            if access_token and "access_token" in command["definition"]["path"]:
                path += f"?access_token={access_token}"
            command["definition"]["path"] = path
            return True
    return False


def copy_attachment(cr, attachment_id, new_res_model, new_res_id):
    """Copy an attachment and link it to a new record."""
    columns = util.get_columns(cr, "ir_attachment", ignore=("id", "res_model", "res_id", "access_token"))
    access_token = str(uuid.uuid4())
    query = util.format_query(
        cr,
        """
        INSERT INTO ir_attachment (
            res_model,
            res_id,
            access_token,
            {columns}
        )
        SELECT %s,
            %s,
            %s,
            {columns}
            FROM ir_attachment
            WHERE id=%s
        RETURNING id, access_token
        """,
        columns=columns,
    )

    cr.execute(query, [new_res_model, new_res_id, access_token, attachment_id])
    return cr.fetchone()
