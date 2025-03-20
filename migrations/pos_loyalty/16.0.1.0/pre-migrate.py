from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "pos.config", "gift_card_settings", {"scan_set": "scan_use"})

    if not util.table_exists(cr, "loyalty_program_pos_config_rel"):
        util.create_m2m(cr, "loyalty_program_pos_config_rel", "loyalty_program", "pos_config")

    # Migrate `coupon_program_ids`, `promo_program_ids` -> properly link to pos_config_ids
    tables = ["pos_config_coupon_program_rel", "pos_config_promo_program_rel"]
    for m2m_relation_table in tables:
        if util.table_exists(cr, m2m_relation_table):
            query = util.format_query(
                cr,
                """
                INSERT INTO loyalty_program_pos_config_rel (pos_config_id, loyalty_program_id)
                     SELECT pos_config_id, loyalty_program_id
                       FROM {}
                ON CONFLICT DO NOTHING
                """,
                m2m_relation_table,
            )
            cr.execute(query)
            cr.execute(util.format_query(cr, "DROP TABLE {}", m2m_relation_table))

    # Migrate `loyalty_program_id`, `gift_card_program_id`
    for field_name in ["loyalty_program_id", "gift_card_program_id"]:
        if util.column_exists(cr, "pos_config", field_name):
            query = util.format_query(
                cr,
                """
                INSERT INTO loyalty_program_pos_config_rel (pos_config_id, loyalty_program_id)
                     SELECT id, {0}
                       FROM pos_config
                      WHERE {0} IS NOT NULL
                ON CONFLICT DO NOTHING
                """,
                field_name,
            )
            cr.execute(query)

    util.remove_field(cr, "pos.config", "use_coupon_programs")
    util.remove_field(cr, "pos.config", "use_gift_card")
    util.remove_field(cr, "pos.config", "coupon_program_ids", drop_column=False)
    util.remove_field(cr, "pos.config", "promo_program_ids", drop_column=False)
    util.remove_field(cr, "pos.config", "loyalty_program_id")
    util.remove_field(cr, "pos.config", "gift_card_program_id")
    util.remove_field(cr, "pos.config", "all_program_ids")
    util.remove_field(cr, "res.config.settings", "pos_loyalty_program_id")
    util.remove_field(cr, "res.config.settings", "pos_use_coupon_programs")
    util.remove_field(cr, "res.config.settings", "pos_coupon_program_ids")
    util.remove_field(cr, "res.config.settings", "pos_promo_program_ids")
    util.remove_field(cr, "res.config.settings", "pos_use_gift_card")
    util.remove_field(cr, "res.config.settings", "pos_gift_card_program_id")
