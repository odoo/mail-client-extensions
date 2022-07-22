# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        "UPDATE res_company SET stock_mail_confirmation_template_id=%s",
        [util.ref(cr, "stock.mail_template_data_delivery_confirmation")],
    )

    util.env(cr)["res.company"].create_missing_scrap_sequence()
    util.update_record_from_xml(cr, "stock.stock_move_rule")
    util.update_record_from_xml(cr, "stock.stock_move_line_rule")

    cr.execute(
        """
        WITH RECURSIVE info(id, complete_name) AS (
             SELECT s.id, s.name
               FROM stock_location s
              WHERE s.usage = 'view'

              UNION ALL

             SELECT s.id,
                    concat(
                        coalesce(info.complete_name,''),
                        '/',
                        coalesce(s.name,'')
                    )
               FROM stock_location s
               JOIN info
                 ON s.location_id = info.id
              WHERE s.usage != 'view'
        ) UPDATE stock_location s
             SET complete_name = info.complete_name
            FROM info
           WHERE s.id = info.id
           """
    )
