# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def update_companies(cr):
    query = """
        WITH _configs AS (
            SELECT company_id, iface_tax_included
              FROM pos_config
             WHERE {}
          GROUP BY company_id, iface_tax_included
        ),
        _uconfigs AS (
            SELECT company_id, iface_tax_included
              FROM _configs
          GROUP BY company_id
            HAVING count(1) = 1
        ),
        _upd1 AS (
            UPDATE res_company c
               SET iface_tax_included = u.iface_tax_included
              FROM _uconfigs u
             WHERE c.id = u.company_id
        )
        SELECT company_id
          FROM _configs
      GROUP BY company_id
        HAGING count(1) > 1
    """

    cr.execute(query.format("true"))
    company_ids = [c[0] for c in cr.fetchall()]
    if company_ids:
        # some configs have differents values for the same company
        # try ignoring deactived and unused configs
        filter_ = """
                company_id IN %s
            AND active = true
            AND id IN (SELECT config_id FROM pos_session)
        """
        cr.execute(query.format(filter_), [tuple(company_ids)])
        company_ids = [c[0] for c in cr.fetchall()]
        if company_ids:
            msg = "Cannot determine unique `Product price on receipts` value for following companies: %r"
            raise util.MigrationError(msg % (company_ids,))

    # unset companies doesn't have a pos_config set.
    cr.execute("UPDATE res_company SET iface_tax_included='subtotal' WHERE iface_tax_included IS NULL")


def migrate(cr, version):
    util.rename_xmlid(cr, "point_of_sale.res_users_form_view", "point_of_sale.res_users_view_form")

    util.rename_field(cr, "pos.config", "iface_invoicing", "module_account_invoicing")
    util.remove_field(cr, "pos.config", "group_sale_pricelist")
    util.remove_field(cr, "pos.config", "group_pricelist_item")

    util.create_column(cr, "res_company", "iface_tax_included", "varchar")
    update_companies(cr)
    util.remove_column(cr, "pos_config", "iface_tax_included")

    env = util.env(cr)
    sales_price = env.user.has_group("product.group_sale_pricelist")
    if not sales_price:
        setting = False
    else:
        setting = "percentage" if env.user.has_group("product.group_product_pricelist") else "formula"

    ICP = env["ir.config_parameter"]
    ICP.set_param("point_of_sale.pos_sales_price", str(sales_price))
    ICP.set_param("point_of_sale.pos_pricelist_setting", setting)
