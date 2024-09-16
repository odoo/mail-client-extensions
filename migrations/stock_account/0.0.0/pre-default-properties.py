from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)

    cr.execute(
        """
        SELECT name, id
          FROM ir_model_fields
         WHERE name in ('property_stock_account_output_categ_id', 'property_stock_account_input_categ_id')
           AND model = 'product.category'
        """
    )

    if util.version_gte("saas~17.5"):
        for name, field_id in cr.fetchall():
            util.ensure_xmlid_match_record(
                cr,
                "stock_account." + name,
                "ir.default",
                {"company_id": env.user.company_id.id, "field_id": field_id},
            )
    else:
        for name, fields_id in cr.fetchall():
            util.ensure_xmlid_match_record(
                cr,
                "stock_account." + name,
                "ir.property",
                {"name": name, "res_id": None, "company_id": env.user.company_id.id, "fields_id": fields_id},
            )
