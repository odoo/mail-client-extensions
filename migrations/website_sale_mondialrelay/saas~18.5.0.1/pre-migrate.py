from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.remove_view(cr, "website_sale_mondialrelay.res_config_settings_view_form")

    util.rename_xmlid(cr, *eb("website_sale_mondialrelay.website_sale_mondialrelay_address_{kanban,card}"))
    util.rename_xmlid(cr, *eb("website_sale_mondialrelay.website_sale_mondialrelay_billing_address_{row,list}"))
