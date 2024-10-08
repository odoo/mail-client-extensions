from odoo.upgrade import util
from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_all=[r"%\_PIVOT%"]):
        new_commands = []
        for command in commands:
            if command["type"] not in ("INSERT_PIVOT", "RE_INSERT_PIVOT", "RENAME_ODOO_PIVOT"):
                new_commands.append(command)
                continue

            # RENAME_ODOO_PIVOT is renamed to RENAME_PIVOT
            if command["type"] == "RENAME_ODOO_PIVOT":
                command["type"] = "RENAME_PIVOT"
                new_commands.append(command)
                continue

            # RE_INSERT_PIVOT is renamed to INSERT_PIVOT, id is renamed to pivotId
            if command["type"] == "RE_INSERT_PIVOT":
                command["type"] = "INSERT_PIVOT"
                command["pivotId"] = command["id"]
                del command["id"]
                new_commands.append(command)
                continue

            # INSERT_PIVOT is split into ADD_PIVOT and INSERT_PIVOT
            definition = command["definition"]
            meta_data = definition.get("metaData", {})
            search_params = definition.get("searchParams", {})
            pivot = {
                "colGroupBys": meta_data.get("colGroupBys", []),
                "rowGroupBys": meta_data.get("rowGroupBys", []),
                "measures": meta_data.get("activeMeasures", []),
                "model": meta_data.get("resModel"),
                "domain": search_params.get("domain", []),
                "context": search_params.get("context", {}),
                "name": definition.get("name"),
                "sortedColumn": meta_data.get("sortedColumn"),
                "type": "ODOO",
            }
            del command["definition"]

            new_commands.append(
                {
                    "type": "ADD_PIVOT",
                    "pivotId": command["id"],
                    "pivot": pivot,
                }
            )
            command["pivotId"] = command["id"]
            del command["id"]
            new_commands.append(command)
        commands.clear()
        commands.extend(new_commands)

    util.rename_field(cr, "spreadsheet.revision", "revision_id", "revision_uuid")
    util.rename_field(cr, "spreadsheet.mixin", "server_revision_id", "current_revision_uuid")
    util.remove_constraint(cr, "spreadsheet_revision", "spreadsheet_revision_parent_revision_unique")
    cr.execute("CREATE INDEX spreadsheet_revision__revision_uuid_index ON spreadsheet_revision(revision_uuid)")

    cr.execute(
        """
        ALTER TABLE spreadsheet_revision RENAME COLUMN parent_revision_id TO _parent_revision_id_upg;
        ALTER TABLE spreadsheet_revision ADD COLUMN parent_revision_id int4;
        """
    )
    util.explode_execute(
        cr,
        """
        UPDATE spreadsheet_revision r
           SET parent_revision_id = p.id
          FROM spreadsheet_revision p
         WHERE p.revision_uuid = r._parent_revision_id_upg
           AND p.res_id = r.res_id
           AND p.res_model = r.res_model
        """,
        table="spreadsheet_revision",
        alias="r",
    )
    cr.execute("ALTER TABLE spreadsheet_revision DROP COLUMN _parent_revision_id_upg")
