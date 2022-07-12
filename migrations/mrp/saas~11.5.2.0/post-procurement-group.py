# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Get MOs linked to bill of materials
    cr.execute(
        """
          SELECT sm.raw_material_production_id
            FROM stock_move sm
            JOIN stock_move p ON p.production_id = sm.raw_material_production_id
        GROUP BY sm.raw_material_production_id
        """
    )
    mo_ids = tuple([id for id, in cr.fetchall()])

    # we should create a new procurement group for each MO in the chain and update related elements.
    if mo_ids:
        util.create_column(cr, "procurement_group", "_tmp", "int4")

        extra_move_cond = "AND sm.purchase_line_id IS NULL" if util.modules_installed(cr, "purchase") else ""
        fields = util.get_columns(cr, "procurement_group", ignore=("id", "name", "sale_id", "_tmp"))
        pg_fields = [f"pg.{c}" for c in fields]

        cr.execute(
            f"""
            INSERT INTO procurement_group (name, _tmp, {','.join(fields)})
                 SELECT mo.name, mo.id, {','.join(pg_fields)}
                   FROM mrp_production mo
                   JOIN procurement_group pg ON pg.id = mo.procurement_group_id
                  WHERE mo.id IN %s
              RETURNING id
            """,
            (mo_ids,),
        )
        new_pg_ids = tuple([id for id, in cr.fetchall()])

        # update MOs to use the new procurement groups
        if new_pg_ids:
            cr.execute(
                """
                   UPDATE mrp_production mo
                      SET procurement_group_id = pg.id
                     FROM procurement_group pg
                    WHERE mo.id = pg._tmp
                      AND pg.id IN %s
                RETURNING mo.id
                """,
                (new_pg_ids,),
            )
            updated_mo_ids = tuple([id for id, in cr.fetchall()])

            # update stock moves and related models to use the new procurement groups
            if updated_mo_ids:
                cr.execute(
                    f"""
                       UPDATE stock_move sm
                          SET group_id = mo.procurement_group_id,
                              name = mo.name
                         FROM mrp_production mo
                        WHERE (sm.raw_material_production_id = mo.id OR sm.production_id = mo.id)
                          AND mo.id IN %s
                          {extra_move_cond}
                    RETURNING sm.id
                    """,
                    (updated_mo_ids,),
                )
                updated_move_ids = tuple([id for id, in cr.fetchall()])

                cr.execute(
                    f"""
                    WITH RECURSIVE moves(id, group_id, picking_id) AS (
                            SELECT sm.id, dm.group_id, sm.picking_id
                              FROM stock_move sm
                              JOIN stock_move_move_rel r ON r.move_orig_id = sm.id
                              JOIN stock_move dm ON dm.id = r.move_dest_id
                             WHERE dm.id IN %s
                                   {extra_move_cond}
                        UNION
                            SELECT sm.id, m.group_id, sm.picking_id
                              FROM stock_move sm
                              JOIN stock_move_move_rel r ON r.move_orig_id = sm.id
                              JOIN moves m ON m.id = r.move_dest_id
                             WHERE true
                                   {extra_move_cond}
                    ),
                    _upg AS (
                        UPDATE stock_picking sp
                           SET group_id = m.group_id
                          FROM moves m
                         WHERE sp.id = m.picking_id
                    )
                    UPDATE stock_move sm
                       SET group_id = m.group_id
                      FROM moves m
                     WHERE sm.id = m.id
                    """,
                    (updated_move_ids,),
                )
                cr.execute(
                    """
                    UPDATE stock_picking p
                       SET group_id = sm.group_id
                      FROM stock_move sm
                     WHERE p.id = sm.picking_id
                       AND sm.id IN %s
                    """,
                    [updated_move_ids],
                )

        util.remove_column(cr, "procurement_group", "_tmp")
