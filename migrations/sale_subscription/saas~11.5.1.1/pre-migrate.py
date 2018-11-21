# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    for event in {"close", "reminder", "success"}:
        util.force_noupdate(cr, "sale_subscription.email_payment_" + event, False)
    for tmpl in {"subscription", "portal_my_subscriptions"}:
        util.force_noupdate(cr, "sale_subscription." + tmpl, False)

    util.remove_record(cr, "sale_subscription.email_subscription_open")
    util.remove_record(cr, "sale_subscription.menu_report_product_all")

    util.rename_xmlid(cr, *eb("sale_subscription.subtype_sta{t,g}e_change"))
    util.rename_xmlid(
        cr,
        "sale_subscription.action_subscription_report_all",
        "sale_subscription.sale_subscription_report_cohort_acion",
    )
    util.rename_xmlid(cr, *eb("sale_subscription.menu_sale_subscription_{lost,close}_reason_action"))

    # model changes
    util.remove_field(cr, "res.config.settings", "module_sale_subscription_dashboard")
    util.remove_field(cr, "res.config.settings", "module_sale_subscription_asset")
    util.remove_view(cr, "sale_subscription.res_config_settings_view_form")
    util.remove_record(cr, "sale_subscription.sale_subscription_config_settings_action")
    util.remove_record(cr, "sale_subscription.sale_subscription_config_settings_menu")

    util.create_column(cr, "sale_subscription", "team_id", "int4")
    util.create_column(cr, "sale_subscription", "percentage_satisfaction", "int4")
    util.create_column(cr, "sale_subscription", "health", "varchar")
    util.create_column(cr, "sale_subscription", "to_renew", "boolean")
    util.create_column(cr, "sale_subscription", "stage_id", "int4")  # fill in post- script
    cr.execute(
        """
        UPDATE sale_subscription
           SET percentage_satisfaction = -1,
               health = 'normal',
               to_renew = (state = 'pending')
    """
    )

    util.create_column(cr, "sale_subscription_template", "payment_mode", "varchar")
    util.create_column(cr, "sale_subscription_template", "auto_close_limit", "int4")
    util.create_column(cr, "sale_subscription_template", "good_health_domain", "varchar")
    util.create_column(cr, "sale_subscription_template", "bad_health_domain", "varchar")
    util.create_column(cr, "sale_subscription_template", "invoice_mail_template_id", "int4")

    cr.execute(
        """
        UPDATE sale_subscription_template
           SET payment_mode = CASE payment_mandatory WHEN true THEN 'success_payment'
                                                     ELSE 'draft_invoice'
                               END,
               auto_close_limit = 15,
               good_health_domain = '[]', bad_health_domain = '[]'
    """
    )

    util.remove_field(cr, "sale.subscription.template", "payment_mandatory")
    util.remove_field(cr, "sale.subscription.report", "recurring_price")
    util.remove_field(cr, "sale.subscription.report", "state")
