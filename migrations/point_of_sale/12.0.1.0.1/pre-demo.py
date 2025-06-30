from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.delete_unused(
        cr,
        "point_of_sale.boni_orange",
        "point_of_sale.peche",
        "point_of_sale.citron",
        "point_of_sale.Onions",
        keep_xmlids=False,
    )
