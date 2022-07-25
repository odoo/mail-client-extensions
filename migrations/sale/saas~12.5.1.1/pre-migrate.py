# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "sale.seq_sale_order", True)
    util.rename_field(cr, "product.attribute", "type", "display_type")

    cr.execute("DELETE FROM product_attribute_custom_value WHERE sale_order_line_id IS NULL")
    util.create_column(cr, "product_attribute_custom_value", "custom_product_template_attribute_value_id", "int4")
    cr.execute(
        """
        UPDATE product_attribute_custom_value c
           SET custom_product_template_attribute_value_id = t.id
          FROM product_template_attribute_value t
         WHERE t.product_attribute_value_id = c.attribute_value_id
    """
    )
    util.remove_field(cr, "product.attribute.custom.value", "attribute_value_id")

    util.create_column(cr, "res_config_settings", "group_auto_done_setting", "boolean")
    util.create_column(cr, "res_config_settings", "module_sale_amazon", "boolean")
    util.remove_field(cr, "res.config.settings", "multi_sales_price")
    util.remove_field(cr, "res.config.settings", "multi_sales_price_method")
    util.remove_field(cr, "res.config.settings", "sale_pricelist_setting")
    util.remove_field(cr, "res.config.settings", "group_sale_order_dates")
    util.remove_field(cr, "res.config.settings", "auto_done_setting")

    cr.execute("DELETE FROM ir_config_parameter WHERE key='sale.sale_pricelist_setting'")

    cr.execute(
        """
        UPDATE sale_order
           SET date_order = confirmation_date
         WHERE state IN ('sale', 'done')
           AND confirmation_date IS NOT NULL
    """
    )

    util.remove_field(cr, "sale.order", "confirmation_date")
    util.remove_field(cr, "sale.report", "confirmation_date")

    cr.execute(
        """
        WITH so_users AS (
            SELECT s.id,COALESCE(p.company_id, u.company_id) as company_id
              FROM sale_order s
        INNER JOIN res_partner p ON s.partner_id=p.id
        INNER JOIN res_users u ON COALESCE(s.user_id, s.create_uid, s.write_uid)=u.id
             WHERE s.company_id IS NULL
        )
        UPDATE sale_order s
           SET company_id=u.company_id
          FROM so_users u
         WHERE s.id=u.id
           AND s.company_id IS NULL
        """
    )
    cr.execute(
        """
        UPDATE sale_order_line l
           SET company_id = o.company_id
          FROM sale_order o
         WHERE o.id = l.order_id
           AND l.company_id != o.company_id
    """
    )

    if util.create_column(cr, "crm_team", "use_quotations", "boolean"):
        cr.execute("UPDATE crm_team SET use_quotations = true")

    util.create_column(cr, "utm_campaign", "company_id", "int4")

    util.remove_record(cr, "sale.group_sale_order_dates")
    util.remove_view(cr, "sale.variants_tree_view")
    util.remove_view(cr, "sale.sale_onboarding_quotation_layout_form")
    util.remove_record(cr, "sale.action_open_sale_onboarding_quotation_layout")

    util.remove_view(cr, "sale.product_pricelist_view_tree")
    util.remove_view(cr, "sale.product_pricelist_view_form")
    util.remove_view(cr, "sale.product_pricelist_view_kanban")

    cr.execute(
        """
        WITH multi_company AS (
            SELECT pt.id AS id
              FROM product_template pt
              JOIN product_product p ON p.product_tmpl_id = pt.id
              JOIN sale_order_line sol ON sol.product_id = p.id
             WHERE pt.company_id IS NOT NULL
               AND sol.company_id IS DISTINCT FROM pt.company_id
        )
        UPDATE product_template
           SET company_id = NULL
          FROM multi_company
         WHERE multi_company.id = product_template.id
    """
    )
