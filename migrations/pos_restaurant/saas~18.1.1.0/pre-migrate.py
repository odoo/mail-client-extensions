from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "pos_restaurant.product_category_pos_food")

    # The pos_takein_preset and pos_takout_preset are only loaded from ui (or in demo mode) using a javascript function
    # https://github.com/odoo/odoo/blob/saas-18.1/addons/point_of_sale/static/src/backend/pos_kanban_view/pos_kanban_view.js#L115
    # in the backend data is loaded in init mode, thus info is updated always
    # https://github.com/odoo/odoo/blob/8b2cf67e32c6584ce36acf952ad298072d863b43/addons/pos_restaurant/models/pos_config.py#L77
    # we insert here the minimal mandatory info
    name_value = util.SQLStr(
        "jsonb_build_object('en_US', %s)" if util.version_gte("saas~18.3") else "%s",
    )

    query = util.format_query(
        cr,
        """
        WITH _preset AS (
            INSERT INTO pos_preset(
                    name, identification, color, slots_per_interval, interval_time
                    )
              VALUES ({name_value}, 'none', '4', '5', '20')
            RETURNING id
        )
        INSERT INTO ir_model_data (module, name, model, noupdate, res_id)
           SELECT 'pos_restaurant', 'pos_takein_preset', 'pos.preset', TRUE,id
             FROM _preset
        RETURNING res_id
        """,
        name_value=name_value,
    )
    cr.execute(query, ["Eat In"])
    eat_in_preset_id = cr.fetchone()[0]

    if util.column_exists(cr, "pos_config", "self_ordering_takeaway"):
        cr.execute("UPDATE pos_config SET takeaway = true WHERE self_ordering_takeaway IS true")

    query = util.format_query(
        cr,
        """
        WITH _presets AS (
           INSERT INTO pos_preset(name, identification,
                                  color, slots_per_interval, interval_time,
                                  fiscal_position_id)
             SELECT {name_value}, 'name',
                    0, 5, 20,
                    takeaway_fp_id
               FROM pos_config
              WHERE takeaway = true
                AND takeaway_fp_id IS NOT NULL
              GROUP BY takeaway_fp_id
                UNION
              SELECT {name_value}, 'name',
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
    """,
        name_value=name_value,
    )
    cr.execute(query, ["Takeout", "Takeout", eat_in_preset_id])

    query = util.format_query(
        cr,
        """
        WITH _preset AS (
            INSERT INTO pos_preset(
                    name, identification, color, slots_per_interval, interval_time
                    )
              VALUES ({name_value}, 'none', '3', '5', '20')
            RETURNING id
        )
        INSERT INTO ir_model_data (module, name, model, noupdate, res_id)
           SELECT 'pos_restaurant', 'pos_takeout_preset', 'pos.preset', TRUE, id
             FROM _preset
        RETURNING res_id
        """,
        name_value=name_value,
    )
    cr.execute(query, ["Takeout"])
    takeout_preset_id = cr.fetchone()[0]

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
    query = util.format_query(
        cr,
        """
        UPDATE pos_order o
            SET preset_id = p.id
          FROM pos_preset p
        WHERE o.takeaway IS true
          AND p.name = {name_value}
          AND o.fiscal_position_id IS NOT DISTINCT FROM p.fiscal_position_id
        """,
        name_value=name_value,
    )
    cr.execute(query, ["Takeout"])

    util.remove_field(cr, "res.config.settings", "pos_takeaway")
    util.remove_field(cr, "res.config.settings", "pos_takeaway_fp_id")
    util.remove_field(cr, "pos.order", "takeaway")
    util.remove_field(cr, "pos.config", "takeaway")
    util.remove_field(cr, "pos.config", "takeaway_fp_id")
