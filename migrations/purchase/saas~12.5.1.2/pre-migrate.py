# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order_line", "display_type", "varchar")
    util.remove_field(cr, "res.config.settings", "group_manage_vendor_price")
    util.create_column(cr, "res_config_settings", "module_purchase_product_matrix", "boolean")

    util.remove_view(cr, "purchase.res_partner_view_purchase_buttons")
    util.remove_view(cr, "purchase.res_partner_view_purchase_account_buttons")

    util.remove_record(cr, "purchase.group_manage_vendor_price")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "purchase.menu_purchase_control"),
            util.ref(cr, "purchase.menu_procurement_management_pending_invoice"),
        ],
    )

    cr.execute(
        """
        WITH po_users AS (
            SELECT o.id,COALESCE(p.company_id, u.company_id) as company_id
              FROM purchase_order o
        INNER JOIN res_partner p ON o.partner_id=p.id
        INNER JOIN res_users u ON COALESCE(o.user_id, o.create_uid, o.write_uid)=u.id
             WHERE o.company_id IS NULL
        )
        UPDATE purchase_order o
           SET company_id=u.company_id
          FROM po_users u
         WHERE o.id=u.id
           AND o.company_id IS NULL
        """
    )

    cr.execute(
        """
        WITH multi_company AS (
            SELECT pt.id AS id
              FROM product_template pt
              JOIN product_product p ON p.product_tmpl_id = pt.id
              JOIN purchase_order_line pol ON pol.product_id = p.id
             WHERE pt.company_id IS NOT NULL
               AND pol.company_id IS DISTINCT FROM pt.company_id
        )
        UPDATE product_template
           SET company_id = NULL
          FROM multi_company
         WHERE multi_company.id = product_template.id
    """
    )
