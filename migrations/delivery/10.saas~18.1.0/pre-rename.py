# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def extract_product(cr, module, carrier_xid, product_xid):
    util.rename_xmlid(
        cr,
        "{}.delivery_carrier_{}_product_product".format(module, carrier_xid),
        "{}.product_product_delivery_{}".format(module, product_xid),
    )
    util.rename_xmlid(
        cr,
        "{}.delivery_carrier_{}_product_template".format(module, carrier_xid),
        "{}.product_product_delivery_{}_product_template".format(module, product_xid),
    )


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("delivery.delivery_{,carrier_}comp_rule"))

    # Carriers defined in `delivery` module does not follow the same pattern as
    # all other `delivery_*` modules and forbid us to use `extract_product` method.
    util.rename_xmlid(cr, "delivery.free_delivery_carrier_product_product", "delivery.product_product_delivery")
    util.rename_xmlid(
        cr, "delivery.free_delivery_carrier_product_template", "delivery.product_product_delivery_product_template"
    )

    # and demo data
    util.rename_xmlid(cr, "delivery.delivery_carrier_product_product", "delivery.product_product_delivery_poste")
    util.rename_xmlid(
        cr, "delivery.delivery_carrier_product_template", "delivery.product_product_delivery_poste_product_template"
    )
    util.rename_xmlid(
        cr, "delivery.normal_delivery_carrier_product_product", "delivery.product_product_delivery_normal"
    )
    util.rename_xmlid(
        cr,
        "delivery.normal_delivery_carrier_product_template",
        "delivery.product_product_delivery_normal_product_template",
    )
