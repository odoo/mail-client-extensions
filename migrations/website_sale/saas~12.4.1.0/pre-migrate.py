# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "website_id", "int4")
    cr.execute(
        """
        UPDATE account_move m
           SET website_id = i.website_id
          FROM account_invoice i
         WHERE i.move_id = m.id
           AND m.website_id IS NULL
    """
    )

    util.create_column(cr, "product_image", "video_url", "varchar")
    util.create_column(cr, "website", "shop_ppg", "int4")
    util.create_column(cr, "website", "shop_ppr", "int4")
    cr.execute("UPDATE website SET shop_ppg = 20, shop_ppr = 4")

    eb = util.expand_braces

    util.rename_xmlid(cr, *eb("website_sale.product_template_{website_tree_view,view_tree}"))
    util.rename_xmlid(cr, *eb("website_sale.search{ count,_count_box}"))  # space is relevant
