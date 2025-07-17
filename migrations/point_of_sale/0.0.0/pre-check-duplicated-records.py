from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~18.1", "19.0"):
        models_to_check = {
            "pos.order": "PoS Order",
            "pos.order.line": "PoS Order Line",
            "pos.payment": "PoS Payment",
        }

        duplicated_records = {}
        for model in models_to_check:
            model_table = model.replace(".", "_")
            cr.execute(
                util.format_query(
                    cr,
                    """
                    SELECT ARRAY_AGG(name ORDER BY id),
                           ARRAY_AGG(id ORDER BY id)
                      FROM {}
                        -- there was a bug that assigned same uuid to all records via
                        -- a default, here we are dealing with records created concurrently
                  GROUP BY uuid
                    HAVING COUNT(*) > 1 AND COUNT(*) < 4
                    """,
                    model_table,
                    model,
                )
            )
            records = cr.fetchall()
            if records:
                duplicated_records[model] = records

        if duplicated_records:
            message = """
                <details>
                    <summary>
                        During the upgrade, we found duplicated records.
                        The duplicated records got newly generated identifiers.
                        If you want to remove them, here are the duplicated records found:
                    </summary>
                    <ul>{}</ul>
                </details>
                """.format(
                "".join(
                    "<li>{}:<ul>{}</ul></li>".format(
                        models_to_check[model],
                        "".join(
                            "<li>{}</li>".format(
                                ", ".join(
                                    util.get_anchor_link_to_record(model, id, name) for id, name in zip(ids, names)
                                )
                            )
                            for names, ids in records
                        ),
                    )
                    for model, records in duplicated_records.items()
                )
            )
            util.add_to_migration_reports(category="Duplicated PoS Records", message=message, format="html")
