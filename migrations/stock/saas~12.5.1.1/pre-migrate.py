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
    cr.execute(
        """
        UPDATE stock_move m
           SET delay_alert = r.delay_alert
          FROM stock_rule r
         WHERE r.id = m.rule_id
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
    util.create_column(cr, "stock_picking_type", "show_reserved", "boolean")
    util.remove_field(cr, "stock.picking.type", "last_done_picking")

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
           SET sequence_code = s.code,
               show_reserved = t.show_operations AND t.code != 'incoming'
          FROM seqcodes s
         WHERE s.id = t.id
    """
    )

    util.create_column(cr, "stock_production_lot", "company_id", "int4")
    # XXX get company of quants?
    cr.execute(
        """
        WITH lot_companies AS (
            SELECT l.id,
                   t.company_id as product_company,
                   c.company_id as create_company,
                   w.company_id as write_company
              FROM stock_production_lot l
         LEFT JOIN product_product p ON p.id = l.product_id
              JOIN product_template t ON t.id = p.product_tmpl_id
         LEFT JOIN res_users c ON c.id = l.create_uid
         LEFT JOIN res_users w ON w.id = l.write_uid
        )
        UPDATE stock_production_lot l
           SET company_id = COALESCE(c.product_company, c.create_company, c.write_company)
          FROM lot_companies c
         WHERE c.id = l.id
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
