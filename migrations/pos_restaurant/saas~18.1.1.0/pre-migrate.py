from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "pos_restaurant.product_category_pos_food")
    eat_in_preset_id = util.ref(cr, "point_of_sale.pos_takein_preset")

    if util.column_exists(cr, "pos_config", "self_ordering_takeaway"):
        cr.execute("UPDATE pos_config SET takeaway = true WHERE self_ordering_takeaway IS true")

    query = """
        WITH _presets AS (
           INSERT INTO pos_preset(name, identification,
                                  color, slots_per_interval, interval_time,
                                  fiscal_position_id)
             SELECT 'Takeout', 'name',
                    0, 5, 20,
                    takeaway_fp_id
               FROM pos_config
              WHERE takeaway = true
                AND takeaway_fp_id IS NOT NULL
              GROUP BY takeaway_fp_id
                UNION
              SELECT 'Takeout', 'name',
                    0, 5, 20,
                    fiscal_position_id
                FROM pos_order
              WHERE takeaway = true
                AND fiscal_position_id IS NOT NULL
              GROUP BY fiscal_position_id
          RETURNING id, fiscal_position_id
        ),
        _upd_config AS (
           UPDATE pos_config c
              SET use_presets = true,
                  default_preset_id = p.id
             FROM _presets p
            WHERE p.fiscal_position_id = c.takeaway_fp_id
        RETURNING c.id, c.default_preset_id
        )
        INSERT INTO pos_config_pos_preset_rel(pos_config_id, pos_preset_id)
             SELECT id, unnest(ARRAY[default_preset_id, %s])
               FROM _upd_config
    """
    cr.execute(query, [eat_in_preset_id])

    takeout_preset_id = util.ref(cr, "point_of_sale.pos_takeout_preset")
    query = """
        WITH _upd AS (
           UPDATE pos_config c
              SET use_presets = true,
                  default_preset_id = %s
            WHERE takeaway = true
              AND takeaway_fp_id IS NULL
        RETURNING id, default_preset_id
        )
        INSERT INTO pos_config_pos_preset_rel(pos_config_id, pos_preset_id)
             SELECT id, unnest(ARRAY[default_preset_id, %s])
               FROM _upd
    """
    cr.execute(query, [takeout_preset_id, eat_in_preset_id])
    cr.execute(
        """
        UPDATE pos_order o
            SET preset_id = p.id
          FROM pos_preset p
        WHERE o.takeaway IS true
          AND p.name = 'Takeout'
          AND o.fiscal_position_id IS NOT DISTINCT FROM p.fiscal_position_id
       """
    )

    util.remove_field(cr, "res.config.settings", "pos_takeaway")
    util.remove_field(cr, "res.config.settings", "pos_takeaway_fp_id")
    util.remove_field(cr, "pos.order", "takeaway")
    util.remove_field(cr, "pos.config", "takeaway")
    util.remove_field(cr, "pos.config", "takeaway_fp_id")
