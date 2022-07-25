# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "stock_putaway_rule", "company_id", "int4")
    cr.execute(
        """
        WITH rule_companies AS (
                SELECT r.id,
                       t.company_id as product_company,
                       i.company_id as locin_company,
                       o.company_id as locout_company,
                       c.company_id as create_company,
                       w.company_id as write_company
                  FROM stock_putaway_rule r
             LEFT JOIN product_product p ON p.id = r.product_id
                  JOIN product_template t ON t.id = p.product_tmpl_id
             LEFT JOIN stock_location i ON i.id = r.location_in_id
             LEFT JOIN stock_location o ON o.id = r.location_out_id
             LEFT JOIN res_users c ON c.id = r.create_uid
             LEFT JOIN res_users w ON w.id = r.write_uid
        )
        UPDATE stock_putaway_rule r
           SET company_id = COALESCE(c.product_company,
                                     c.locin_company, c.locout_company,
                                     c.create_company, c.write_company)
          FROM rule_companies c
         WHERE c.id = r.id
    """
    )

    util.create_column(cr, "res_company", "stock_move_email_validation", "boolean")
    util.create_column(cr, "res_company", "stock_mail_confirmation_template_id", "int4")

    util.create_column(cr, "res_config_settings", "module_stock_sms", "boolean")
    util.create_column(cr, "res_config_settings", "module_delivery", "boolean")

    util.create_column(cr, "stock_inventory", "prefill_counted_quantity", "varchar")
    cr.execute("UPDATE stock_inventory SET prefill_counted_quantity='counted'")

    util.create_column(cr, "stock_inventory_line", "categ_id", "int4")
    cr.execute(
        """
        UPDATE stock_inventory_line l
           SET categ_id = t.categ_id
          FROM product_product p, product_template t
         WHERE p.id = l.product_id
           AND t.id = p.product_tmpl_id
    """
    )

    util.remove_field(cr, "stock.move", "product_packaging")
    util.create_column(cr, "stock_move", "delay_alert", "boolean")
    util.create_column(cr, "stock_move", "next_serial", "varchar")
    util.create_column(cr, "stock_move", "next_serial_count", "int4")

    util.create_column(cr, "stock_rule", "delay_alert", "boolean")
    cr.execute(
        """
        UPDATE stock_rule r
           SET delay_alert = (p.code = 'outgoing')
          FROM stock_picking_type p
         WHERE p.id = r.picking_type_id
    """
    )
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
                UPDATE stock_move m
                   SET delay_alert = r.delay_alert
                  FROM stock_rule r
               WHERE r.id = m.rule_id
            """,
            table="stock_move",
            prefix="m.",
        ),
    )

    cr.execute(
        """
        WITH warehouse_ids AS (
             SELECT warehouse.id, warehouse.company_id
               FROM stock_warehouse warehouse
               JOIN stock_rule rule ON rule.warehouse_id = warehouse.id
             GROUP BY warehouse.id, warehouse.company_id
        )
        UPDATE stock_rule rule1
           SET company_id=ware_id.company_id
          FROM warehouse_ids ware_id
         WHERE rule1.warehouse_id=ware_id.id
        """
    )

    cr.execute(
        """
         WITH package_companies AS (
                   SELECT package.id,
                          location.company_id as location_company_id,
                          (ARRAY_AGG(quant.company_id))[1] as quant_company_id,
                          (ARRAY_AGG(template.company_id))[1] as product_company_id
                     FROM stock_quant_package package
                     JOIN stock_location location ON location.id = package.location_id
                     JOIN stock_quant quant ON quant.package_id = package.id
                     JOIN product_product product ON product.id = quant.product_id
                     JOIN product_template template ON template.id = product.product_tmpl_id
                 GROUP BY package.id, location.id
         )
         UPDATE stock_quant_package package
            SET company_id = COALESCE(c.location_company_id, c.quant_company_id, c.product_company_id)
           FROM package_companies c
          WHERE c.id = package.id AND package.company_id IS NULL
         """
    )
    util.create_column(cr, "stock_package_level", "company_id", "int4")
    cr.execute(
        """
        WITH level_companies AS (
            SELECT l.id,
                   pa.company_id as package_company,
                   pi.company_id as picking_company,
                   loc.company_id as location_company,
                   c.company_id as create_company,
                   w.company_id as write_company
              FROM stock_package_level l
              JOIN stock_quant_package pa ON pa.id = l.package_id
         LEFT JOIN stock_picking pi ON pi.id = l.picking_id
         LEFT JOIN stock_location loc ON loc.id = l.location_dest_id
         LEFT JOIN res_users c ON c.id = l.create_uid
         LEFT JOIN res_users w ON w.id = l.write_uid
        )
        UPDATE stock_package_level l
           SET company_id = COALESCE(c.package_company, c.picking_company, c.location_company,
                                     c.create_company, c.write_company)
         FROM level_companies c
        WHERE c.id = l.id
    """
    )

    util.create_column(cr, "stock_picking_type", "sequence_code", "varchar")
    util.create_column(cr, "stock_picking_type", "return_picking_type_id", "int4")
    show_reserved_created = util.create_column(cr, "stock_picking_type", "show_reserved", "boolean")
    util.remove_field(cr, "stock.picking.type", "last_done_picking")

    dashdash = "" if show_reserved_created else "--"

    cr.execute(
        r"""
        WITH seqcodes AS (
            SELECT t.id,
                   COALESCE((regexp_match(s.prefix,
                                          CONCAT('^',
                                                 CASE WHEN w.id IS NOT NULL
                                                   THEN CONCAT(regexp_replace(w.code, '(\W)', '\\\1', 'g'), '/(.*)/')
                                                   ELSE '(.*)'
                                                 END,
                                                 '$')
                                          ))[1],
                            s.prefix) as code
              FROM stock_picking_type t
              JOIN ir_sequence s ON s.id = t.sequence_id
         LEFT JOIN stock_warehouse w ON w.id = t.warehouse_id
        )
        UPDATE stock_picking_type t
           SET sequence_code = s.code
               {}, show_reserved = t.show_operations AND t.code != 'incoming'
          FROM seqcodes s
         WHERE s.id = t.id
    """.format(
            dashdash
        )
    )

    util.create_column(cr, "stock_production_lot", "company_id", "int4")
    # XXX get company of quants?
    cr.execute(
        """
        WITH lot_companies AS (
            SELECT DISTINCT ON (l.id)
                   l.id,
                   sml.company_id as sml_company,
                   t.company_id as product_company,
                   c.company_id as create_company,
                   w.company_id as write_company
              FROM stock_production_lot l
         LEFT JOIN stock_move_line sml ON l.id = sml.lot_id
         LEFT JOIN product_product p ON p.id = l.product_id
              JOIN product_template t ON t.id = p.product_tmpl_id
         LEFT JOIN res_users c ON c.id = l.create_uid
         LEFT JOIN res_users w ON w.id = l.write_uid
         ORDER BY l.id, sml.date DESC
        )
        UPDATE stock_production_lot l
           SET company_id = COALESCE(c.sml_company, c.product_company, c.create_company, c.write_company)
          FROM lot_companies c
         WHERE c.id = l.id
         AND l.company_id IS NULL
    """
    )

    util.create_column(cr, "stock_scrap", "company_id", "int4")
    util.create_column(cr, "stock_scrap", "date_done", "timestamp without time zone")
    util.remove_field(cr, "stock.scrap", "date_expected")
    cr.execute(
        """
        WITH scrap_companies AS (
            SELECT s.id,
                   t.company_id as product_company,
                   pa.company_id as package_company,
                   pi.company_id as picking_company,
                   l.company_id as location_company,
                   sl.company_id as scrap_location_company,
                   o.company_id as owner_company,
                   c.company_id as create_company,
                   w.company_id as write_company,
                   pi.date_done
              FROM stock_scrap s
         LEFT JOIN product_product p ON p.id = s.product_id
              JOIN product_template t ON t.id = p.product_tmpl_id
         LEFT JOIN stock_quant_package pa ON pa.id = s.package_id
         LEFT JOIN stock_picking pi ON pi.id = s.picking_id
              JOIN stock_location l ON l.id = s.location_id
              JOIN stock_location sl ON sl.id = s.scrap_location_id
         LEFT JOIN res_partner o ON o.id = s.owner_id
         LEFT JOIN res_users c ON c.id = s.create_uid
         LEFT JOIN res_users w ON w.id = s.write_uid
        )
        UPDATE stock_scrap s
           SET company_id = COALESCE(c.product_company,
                                     c.scrap_location_company, c.location_company,
                                     c.package_company, c.picking_company,
                                     c.owner_company, c.create_company, c.write_company),
               date_done = CASE state WHEN 'done' THEN c.date_done END
          FROM scrap_companies c
         WHERE c.id = s.id
    """
    )

    util.create_column(cr, "stock_warehouse", "sequence", "int4")
    cr.execute("UPDATE stock_warehouse SET sequence=id")

    # wizards
    util.create_column(cr, "product_replenish", "company_id", "int4")
    util.rename_field(cr, "stock.quantity.history", "date", "inventory_datetime")
    util.remove_field(cr, "stock.quantity.history", "compute_at_date")

    util.remove_model(cr, "report.stock.forecast")

    util.convert_field_to_property(cr, "product.template", "responsible_id", type="many2one", target_model="res.users")

    # stock move line
    cr.execute(
        """
           UPDATE stock_move_line l
              SET company_id = p.company_id
              FROM stock_picking p
              WHERE l.picking_id = p.id
              AND l.company_id IS NULL
              AND l.move_id IS NULL
         """
    )

    cr.execute(
        """
      WITH multi_company AS (
            SELECT pt.id AS id
              FROM product_template pt
              JOIN product_product p ON p.product_tmpl_id = pt.id
              JOIN stock_move sm ON sm.product_id = p.id
             WHERE pt.company_id IS NOT NULL
               AND sm.company_id IS DISTINCT FROM pt.company_id
          UNION
            SELECT pt.id AS id
              FROM product_template pt
              JOIN product_product p ON p.product_tmpl_id = pt.id
              JOIN stock_move_line sml ON sml.product_id = p.id
             WHERE pt.company_id IS NOT NULL
               AND sml.company_id IS DISTINCT FROM pt.company_id
        )
        UPDATE product_template
           SET company_id = NULL
          FROM multi_company
         WHERE multi_company.id = product_template.id
     """
    )
