from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "quality.check.on.demand")
    util.remove_field(cr, "quality.check", "spreadsheet_check_cell")
    util.create_column(cr, "quality_check", "spreadsheet_template_id", "int4")

    util.explode_execute(
        cr,
        """
        UPDATE quality_check qc
           SET spreadsheet_template_id = qp.spreadsheet_template_id
          FROM quality_point qp
         WHERE qp.id = qc.point_id
           AND qp.spreadsheet_template_id IS NOT NULL
        """,
        table="quality_check",
        alias="qc",
    )

    cols = ["picking_id"]
    if util.column_exists(cr, "quality_check", "production_id"):  # quality_mrp installed
        cols.append("production_id")
    if util.column_exists(cr, "quality_check", "repair_id"):  # quality_repair installed
        cols.append("repair_id")
    columns = util.ColumnList.from_unquoted(cr, cols)

    if len(cols) > 1:
        query = util.format_query(
            cr,
            """
            SELECT qc.id,
                   qc.name
              FROM quality_check qc
             WHERE cardinality(array_remove(array[{}], NULL)) > 1;
            """,
            columns,
        )
        cr.execute(query)

        if cr.rowcount:
            li = " ".join([util.get_anchor_link_to_record("quality.check", id, name) for (id, name) in cr.fetchall()])
            msg = f"""
                <details>
                <summary>
                    Some Quality Checks have a combination of Transfers, Repair Orders,
                    and/or Manufacturing Orders linked to them. At most one of them
                    should be linked at a time. Quality Checks that have more than one
                    may get validation errors when modifying them in Odoo 19.

                    Below there is a list of the faulty records. Please check them and
                    ensure the linked transfers or orders are correct.
                </summary>
                <ul>{li}</ul>
                </details>
            """
            util.add_to_migration_reports(category="Quality", message=msg, format="html")
