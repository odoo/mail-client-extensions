# -*- coding: utf-8 -*-
import os

from odoo.addons.base.maintenance.migrations import util

# BoMs with zero product_qty are not allowed from 13.0 up.
# If this variable is set, we fix the BoMs automatically by changing the quantity
# from 0 to 1
UPDATE_BOMS = util.str2bool(os.environ.get("ODOO_MIG_UPDATE_ZERO_QUANTITY_BOMS", "0"))


def migrate(cr, version):
    if util.version_gte("13.0"):
        _check_zero_boms(cr)


def _check_zero_boms(cr):
    cr.execute(
        """
        SELECT b.id,
               pt.name
          FROM mrp_bom b
          JOIN product_template pt
            ON b.product_tmpl_id = pt.id
         WHERE b.product_qty <= 0
        """
    )
    info = cr.fetchall()
    if not info:
        return
    if UPDATE_BOMS:
        cr.execute("UPDATE mrp_bom SET product_qty=1 WHERE id IN %s", [tuple(r[0] for r in info)])
        util.add_to_migration_reports(
            message="""
            <details>
            <summary>
                While upgrading your database we have detected some Bill of Materials that have zero
                Quantity of produced products. To allow the upgrade, we have set the quantity to 1.
            </summary>
            Note: this action was activated with the environment variable ODOO_MIG_UPDATE_ZERO_QUANTITY_BOMS
            List of updated BoMs:
            <ol>{}</ol>
            </details>
            """.format(
                "\n".join("<li>{}</li>".format(util.get_anchor_link_to_record("mrp.bom", r[0], r[1])) for r in info)
            ),
            category="MRP",
            format="html",
        )
        return
    msg = """
    Bills of Materials (BoM) with zero Quantity are not allowed. To be able to continue the upgrade, you can:
    - fix these inconsistencies manually (below the details of the affected BoMs)
    OR
    - let this script automatically set the quantity to 1 on the affected BoMs by setting the environment variable
      ODOO_MIG_UPDATE_ZERO_QUANTITY_BOMS to 1

    The BoMs with zero produced quantity are:
    {}
    """.format("\n".join("    * {} (product: {})".format(*r) for r in info))
    raise util.MigrationError(msg)
