# -*- coding: utf-8 -*-
from odoo.upgrade import util
from odoo.upgrade.util import inconsistencies


def migrate(cr, version):
    # In case where the `website_sale` module is installed and `delivery` IS NOT , it will be installed
    # in database where upgrade target >= `saas~16.2` as `website_sale` now depends on `delivery`.
    # At `delivery` install, computation of field `sale.order.line.product_qty` can raise uom error that
    # is not catchable by an upgrade scripts (as new installation, no upgrade script is run). As an error
    # will happen if inconsistencies are found, raise now avoid time waste
    if (
        util.module_installed(cr, "website_sale")
        and not util.module_installed(cr, "delivery")
        and inconsistencies.verify_uoms(cr, "sale.order.line", uom_field="product_uom")
    ):
        raise util.MigrationError("Inconsistent UoMs, cannot install new dependency 'delivery' of 'website_sale'")
