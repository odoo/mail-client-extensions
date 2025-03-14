from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.team", "use_quotations")

    eb = util.expand_braces
    xmlids = [
        "variants",
        "badge_extra_price",
    ]
    if util.module_installed(cr, "website_sale"):
        for xmlid in xmlids:
            util.rename_xmlid(
                cr,
                *eb("{,website_}sale." + xmlid),
            )
    else:
        for xmlid in xmlids:
            util.remove_view(cr, "sale." + xmlid)
