from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "quality.check.on.demand")
    util.remove_field(cr, "quality.check", "spreadsheet_check_cell")
    util.create_column(cr, "quality_check", "spreadsheet_template_id", "int4")

    query = False
    if util.column_exists(cr, "quality_check", "production_id") and util.column_exists(
        cr, "quality_check", "repair_id"
    ):
        query = """
            SELECT qc.id, qc.name
              FROM quality_check qc
             WHERE (qc.picking_id IS NOT NULL AND qc.production_id IS NOT NULL)
                OR (qc.picking_id IS NOT NULL AND qc.repair_id IS NOT NULL)
                OR (qc.production_id IS NOT NULL AND qc.repair_id IS NOT NULL);
        """
    elif util.column_exists(cr, "quality_check", "production_id"):
        query = """
            SELECT qc.id, qc.name
              FROM quality_check qc
             WHERE (qc.picking_id IS NOT NULL AND qc.production_id IS NOT NULL);
        """
    elif util.column_exists(cr, "quality_check", "repair_id"):
        query = """
            SELECT qc.id, qc.name
              FROM quality_check qc
             WHERE (qc.picking_id IS NOT NULL AND qc.repair_id IS NOT NULL);
        """

    if query:
        cr.execute(query)
        if cr.rowcount:
            util.add_to_migration_reports(
                category="Quality",
                message=(
                    f"""
                <span>
            There are some Quality Checks that have a combination of Transfers, Repair Orders,
            and/or Manufacturing Orders linked to them. It is expected that only one at most of
            these is linked to a Quality Check at a time. Quality Checks that have more than 1
            assigned to them many have validation errors if the extra linkages are not removed
            when modifying them after this upgrade.
            The following are the faulty records:\n<ul>{
                        " ".join(
                            [util.get_anchor_link_to_record("quality.check", id, name) for (id, name) in cr.fetchall()]
                        )
                    }</ul>
            </span>
                """
                ),
                format="html",
            )
