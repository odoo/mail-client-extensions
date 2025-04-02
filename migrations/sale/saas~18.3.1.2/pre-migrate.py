from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.config.settings", "module_sale_gelato", "sale_gelato", "sale")
    util.remove_field(cr, "sale.order.discount", "tax_ids")

    util.rename_xmlid(cr, *util.expand_braces("sale.{,send_pending_emails_}cron"))

    util.remove_field(cr, "res.partner", "sale_warn")
    util.remove_field(cr, "product.template", "sale_line_warn")

    util.remove_field(cr, "res.config.settings", "module_delivery_fedex")
    util.remove_field(cr, "res.config.settings", "module_delivery_ups")
    util.remove_field(cr, "res.config.settings", "module_delivery_usps")
    util.remove_field(cr, "crm.team", "quotations_count")
    util.remove_field(cr, "crm.team", "quotations_amount")
    util.remove_field(cr, "crm.team", "sales_to_invoice_count")
    util.remove_view(cr, "sale.crm_lead_partner_kanban_view")

    util.replace_record_references(
        cr,
        ("mail.activity.type", util.ref(cr, "sale.mail_act_sale_upsell")),
        ("mail.activity.type", util.ref(cr, "mail.mail_activity_data_todo")),
        replace_xmlid=False,
    )
    util.delete_unused(cr, "sale.mail_act_sale_upsell")
