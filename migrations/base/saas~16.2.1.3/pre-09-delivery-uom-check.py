# -*- coding: utf-8 -*-
import os

from odoo.upgrade import util
from odoo.upgrade.util import inconsistencies

fix_inconsistencies_method = util.str2bool(os.environ.get("ODOO_MIG_FIX_SOL_UOM_INCONSISTENCIES", "0"))


def fix_uom_in_so_lines(cr, faulty_ids):
    cr.execute(
        """
        WITH actual_uoms AS(
            SELECT sol.id AS sol_id, pt.uom_id AS pt_uom
              FROM sale_order_line sol
              JOIN product_product pp
                ON pp.id = sol.product_id
              JOIN product_template pt
                ON pt.id = pp.product_tmpl_id
             WHERE sol.id IN %s
        )
        UPDATE sale_order_line sol
           SET product_uom = au.pt_uom
          FROM actual_uoms au
         WHERE au.sol_id = sol.id
        """,
        [tuple(faulty_ids)],
    )
    util.add_to_migration_reports(
        """
        There was a mismatch in the Unit of Measure of some Sale Order Lines.
        The category of the UoM in the lines didn't match the UoM category of the product in the lines.
        The UoM in the faulty Sale Order Lines have been automatically updated from its linked products.
        Here is the List of faulty Sale Order Lines IDs = {}
        """.format(
            faulty_ids
        )
    )


def migrate(cr, version):
    # In case where the `website_sale` module is installed and `delivery` IS NOT , it will be installed
    # in database where upgrade target >= `saas~16.2` as `website_sale` now depends on `delivery`.
    # At `delivery` install, computation of field `sale.order.line.product_qty` can raise uom error that
    # is not catchable by an upgrade scripts (as new installation, no upgrade script is run). As an error
    # will happen if inconsistencies are found, raise now avoid time waste
    if util.module_installed(cr, "website_sale") and not util.module_installed(cr, "delivery"):
        faulty_ids = inconsistencies.verify_uoms(cr, "sale.order.line", uom_field="product_uom")
        if not faulty_ids:
            return
        if fix_inconsistencies_method:
            fix_uom_in_so_lines(cr, faulty_ids)
        else:
            raise util.MigrationError("Inconsistent UoMs, cannot install new dependency 'delivery' of 'website_sale'")
