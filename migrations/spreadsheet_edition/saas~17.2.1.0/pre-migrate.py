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

    cr.execute(
        r"""
        WITH RECURSIVE info AS (
            -- get the last snapshot per reference record
            SELECT max(sr.id) FILTER(WHERE sr.commands LIKE '%SNAPSHOT\_CREATED%') AS id
              FROM spreadsheet_revision sr
         LEFT JOIN spreadsheet_revision sr2
                ON sr.parent_revision_id = sr2.revision_id
                -- if there is a change of reference record
                -- the revision can be considered as a head revision
               AND sr.res_id = sr2.res_id
               AND sr.res_model = sr2.res_model
          GROUP BY sr.res_id, sr.res_model
            -- restrict to cases with more than one revision with missing parent
            -- note: the head revision will always have a missing parent
            HAVING COUNT(*) FILTER(WHERE sr2.id IS NULL) > 1
        ), hierarchy AS (
            -- starting from the last snapshot
            SELECT s.id,
                   s.revision_id,
                   s.res_id,
                   s.res_model
              FROM spreadsheet_revision s
              JOIN info
                ON s.id = info.id

             UNION ALL

            SELECT t.id,
                   t.revision_id,
                   t.res_id,
                   t.res_model
              FROM spreadsheet_revision t
              JOIN hierarchy h
                ON t.parent_revision_id = h.revision_id
               AND t.res_id = h.res_id
               AND t.res_model = h.res_model
        ), grouped AS (
            SELECT res_id,
                   res_model,
                   array_agg(id) AS ids
              FROM hierarchy
          GROUP BY res_id, res_model
        )
            -- remove all revisions that are not in a unbroken straight line
            -- from the last snapshot of each record (res_model/id)
       DELETE FROM spreadsheet_revision sr
             USING grouped
             WHERE sr.id != ALL(grouped.ids)
               AND sr.res_id = grouped.res_id
               AND sr.res_model = grouped.res_model
        """
    )

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
