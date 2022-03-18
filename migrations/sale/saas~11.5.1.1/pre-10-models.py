# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "so_reference_type", "varchar")
    cr.execute("UPDATE payment_acquirer set so_reference_type='so_name'")

    util.create_column(cr, "res_company", "portal_confirmation_sign", "boolean")
    util.create_column(cr, "res_company", "portal_confirmation_pay", "boolean")
    util.create_column(cr, "res_company", "quotation_validity_days", "int4")
    util.create_column(cr, "res_company", "sale_quotation_onboarding_state", "varchar")
    util.create_column(cr, "res_company", "sale_onboarding_order_confirmation_state", "varchar")
    util.create_column(cr, "res_company", "sale_onboarding_sample_quotation_state", "varchar")
    util.create_column(cr, "res_company", "sale_onboarding_payment_method", "varchar")
    # TODO: compute correct onboarding
    cr.execute(
        """
        WITH conf_option AS (
            DELETE FROM ir_config_parameter
                  WHERE key='sale.sale_portal_confirmation_options'
              RETURNING value
        )
        UPDATE res_company c
        SET quotation_validity_days=30,
            portal_confirmation_sign = (select * from conf_option) = 'sign',
            portal_confirmation_pay = (select * from conf_option) = 'pay',
            sale_quotation_onboarding_state='not_done',
            sale_onboarding_order_confirmation_state=payment_acquirer_onboarding_state,
            sale_onboarding_sample_quotation_state=EXISTS(
                SELECT 1 FROM sale_order WHERE state='sent' AND company_id = c.id
            )
    """
    )

    util.create_column(cr, "res_config_settings", "use_quotation_validity_days", "boolean")
    util.create_column(cr, "res_config_settings", "portal_confirmation_sign", "boolean")
    util.create_column(cr, "res_config_settings", "portal_confirmation_pay", "boolean")
    util.create_column(cr, "res_config_settings", "group_sale_order_dates", "boolean")
    util.move_field_to_module(cr, "res.config.settings", "automatic_invoice", "website_sale", "sale")
    util.create_column(cr, "res_config_settings", "automatic_invoice", "boolean")
    util.create_column(cr, "res_config_settings", "template_id", "int4")
    util.remove_field(cr, "res.config.settings", "portal_confirmation")
    util.remove_field(cr, "res.config.settings", "portal_confirmation_options")
    util.remove_field(cr, "res.config.settings", "module_sale_payment")
    util.remove_field(cr, "res.config.settings", "module_website_quote")
    util.remove_field(cr, "res.config.settings", "group_sale_layout")
    util.remove_field(cr, "res.config.settings", "group_show_price_subtotal")
    util.remove_field(cr, "res.config.settings", "group_show_price_total")
    util.remove_field(cr, "res.config.settings", "sale_show_tax")

    ICP = util.env(cr)["ir.config_parameter"]
    ICP.set_param("sale.default_email_template", util.ref(cr, "account.email_template_edi_invoice"))

    util.create_column(cr, "sale_order", "reference", "varchar")
    util.create_column(cr, "sale_order", "currency_rate", "float8")
    util.create_column(cr, "sale_order", "signed_by", "varchar")
    util.create_column(cr, "sale_order", "commitment_date", "timestamp without time zone")
    util.remove_field(cr, "sale.order", "product_id")

    util.move_field_to_module(cr, "sale.order", "amount_undiscounted", "sale_quotation_builder", "sale")
    util.move_field_to_module(cr, "sale.order", "require_payment", "sale_quotation_builder", "sale")
    util.create_column(cr, "sale_order", "require_signature", "boolean")
    if not util.column_exists(cr, "sale_order", "require_payment"):
        util.create_column(cr, "sale_order", "require_payment", "boolean")
        util.parallel_execute(
            cr,
            util.explode_query_range(
                cr,
                """
            WITH reqs AS (
                SELECT o.id,
                       COALESCE(oc.portal_confirmation_pay, uc.portal_confirmation_pay) as pay,
                       COALESCE(oc.portal_confirmation_sign, uc.portal_confirmation_sign) as sign
                  FROM sale_order o
             LEFT JOIN res_company oc ON oc.id = o.company_id
             LEFT JOIN res_users u ON u.id = o.create_uid
                  JOIN res_company uc ON uc.id = u.company_id
                 WHERE {parallel_filter}
            )
            UPDATE sale_order o
               SET require_payment = r.pay,
                   require_signature = r.sign
              FROM reqs r
             WHERE r.id = o.id
                """,
                table="sale_order",
                alias="o",
            ),
        )
    else:
        # existing column is int4; change type.
        cr.execute(
            """
            ALTER TABLE sale_order
           ALTER COLUMN require_payment
                   TYPE boolean
                  USING require_payment::boolean
        """
        )
        util.parallel_execute(
            cr,
            util.explode_query(
                cr,
                "UPDATE sale_order SET require_signature=true WHERE COALESCE(require_payment, false) = false",
            ),
        )

    util.create_column(cr, "sale_order_line", "untaxed_amount_invoiced", "numeric")
    util.create_column(cr, "sale_order_line", "untaxed_amount_to_invoice", "numeric")

    util.move_field_to_module(cr, "product.attribute", "type", "website_sale", "sale")
    util.move_field_to_module(cr, "product.attribute.value", "html_color", "website_sale", "sale")

    util.remove_field(cr, "sale.report", "amount_to_invoice")
    util.remove_field(cr, "sale.report", "amount_invoiced")
