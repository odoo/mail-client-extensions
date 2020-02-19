# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    ICP = util.env(cr)["ir.config_parameter"]

    util.create_column(cr, "account_invoice", "website_id", "int4")
    # website_id on res_partner is a new field in saas-11.5,
    # no need to recompute the stored related, it's always NULL
    util.rename_field(cr, "res.config.settings", "module_account_invoicing", "module_account")
    util.remove_field(cr, "res.config.settings", "automatic_invoice")
    util.remove_field(cr, "res.config.settings", "module_l10n_eu_service")

    util.create_column(cr, "website", "cart_recovery_mail_template_id", "int4")
    tmpl_id = util.ref(cr, "website_sale.mail_template_sale_cart_recovery")
    from_config_tmpl_id = int(ICP.get_param("website_sale.cart_recovery_mail_template_id") or 0)
    if tmpl_id and from_config_tmpl_id == tmpl_id:
        util.ENVIRON["S115_default_cart_recovery_template"] = True
        from_config_tmpl_id = None

    if from_config_tmpl_id:
        cr.execute("UPDATE website SET cart_recovery_mail_template_id=%s", [from_config_tmpl_id])
    util.if_unchanged(cr, "website_sale.mail_template_sale_cart_recovery", util.update_record_from_xml)

    util.create_column(cr, "website", "cart_abandoned_delay", "float8")
    delay = ICP.get_param("website_sale.cart_abandoned_delay")
    if delay:
        cr.execute("UPDATE website SET cart_abandoned_delay=%s", [delay])

    util.remove_column(cr, "res_partner", "last_website_so_id")

    util.remove_field(cr, "sale.order", "can_directly_mark_as_paid")
    util.create_column(cr, "sale_order", "website_id", "int4")
    # Still no need to compute it, for the exact same reason

    util.remove_view(cr, "website_sale.sale_order_view_form")
    util.remove_view(cr, "website_sale.sort")
    util.remove_view(cr, "website_sale.content_new_product")
