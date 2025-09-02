# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_gte("saas~18.1"):
        _activate_reference_uom(cr)


def _activate_reference_uom(cr):
    uom_table, category_table = (
        ("uom_uom", "uom_category") if util.table_exists(cr, "uom_uom") else ("product_uom", "product_uom_categ")
    )

    query = util.format_query(
        cr,
        """
        WITH cats_single_ref AS (
            SELECT category_id as id
              FROM {uom_table}
             WHERE uom_type = 'reference'
          GROUP BY category_id
            HAVING COUNT(category_id) = 1
        )
        UPDATE {uom_table} u
           SET active = True
          FROM cats_single_ref ref
          JOIN {category_table} c
            ON c.id = ref.id
         WHERE c.id = u.category_id
           AND u.uom_type = 'reference'
           AND u.active = False
     RETURNING u.{uom_col}, c.{categ_col}
        """,
        uom_table=uom_table,
        category_table=category_table,
        uom_col=util.get_value_or_en_translation(cr, uom_table, "name"),
        categ_col=util.get_value_or_en_translation(cr, category_table, "name"),
    )
    cr.execute(query)
    activated_uoms = cr.fetchall()
    if activated_uoms:
        util.add_to_migration_reports(
            message="UoM Categories must have a reference unit. The following reference units "
            "were reactivated: {}".format(
                ", ".join("{} from category {}".format(unit, cat) for unit, cat in activated_uoms)
            ),
            category="Units of Measure",
        )
