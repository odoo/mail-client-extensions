from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mail_plugin.res_partner_iap_view_tree")
    util.remove_view(cr, "mail_plugin.res_partner_iap_view_form")

    util.remove_field(cr, "res.config.settings", "module_mail_plugin")

    util.remove_field(cr, "res.partner", "iap_enrich_info")
    util.remove_field(cr, "res.partner", "iap_search_domain")

    util.remove_model(cr, "res.partner.iap")
