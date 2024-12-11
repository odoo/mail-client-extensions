import os

from odoo.upgrade import util
from odoo.upgrade.util import inconsistencies

fix_sol_inconsistencies = util.str2bool(os.environ.get("ODOO_MIG_FIX_SOL_UOM_INCONSISTENCIES", "0"))


def fix_uom_in_so_lines(cr):
    faulty_ids = inconsistencies.verify_uoms(cr, "sale.order.line", uom_field="product_uom")
    if not faulty_ids:
        return
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
        """.format(faulty_ids)
    )


def migrate(cr, version):
    if fix_sol_inconsistencies:
        fix_uom_in_so_lines(cr)

    util.remove_field(cr, "sale.order.cancel", "email_from")
    util.remove_field(cr, "res.config.settings", "use_quotation_validity_days")
    util.remove_column(cr, "res_config_settings", "deposit_default_product_id")

    env = util.env(cr)
    ICP = env["ir.config_parameter"]
    util.remove_constraint(cr, "res_company", "res_company_check_quotation_validity_days")
    use_quotation_validity_days = util.str2bool(ICP.get_param("sale.use_quotation_validity_days"))
    if not use_quotation_validity_days:
        cr.execute("""UPDATE res_company SET quotation_validity_days = 0""")

    default_deposit_product_id = ICP.get_param("sale.default_deposit_product_id", default=False)
    util.create_column(cr, "res_company", "sale_down_payment_product_id", "int4")
    if default_deposit_product_id:
        cr.execute(
            """
            UPDATE res_company rc
               SET sale_down_payment_product_id = pp.id
              FROM product_template pt
              JOIN product_product pp
                ON pp.product_tmpl_id = pt.id
             WHERE pp.id = %s
               AND COALESCE(pt.company_id, rc.id) = rc.id
               AND pt.type = 'service'
               AND pt.invoice_policy = 'order'
            """,
            [default_deposit_product_id],
        )
    cr.execute(
        """
        DELETE FROM ir_config_parameter
        WHERE key in ('sale.use_quotation_validity_days', 'sale.default_deposit_product_id')
        """
    )
    util.rename_xmlid(cr, "sale.view_order_tree", "sale.sale_order_tree")

    util.create_column(cr, "sale_order", "amount_to_invoice", "numeric")  # computed in `post-` script
