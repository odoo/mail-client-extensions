from odoo.upgrade import util


def migrate(cr, version):
    # Link the products to slas.
    util.create_m2m(cr, "helpdesk_sla_product_template_rel", "product_template", "helpdesk_sla")
    cr.execute(
        util.format_query(
            cr,
            """
            INSERT INTO helpdesk_sla_product_template_rel(product_template_id, helpdesk_sla_id)
                 SELECT DISTINCT SPLIT_PART(ip.res_id, ',', 2)::int AS product_template_id,
                        SPLIT_PART(ip.value_reference, ',', 2)::int AS helpdesk_sla_id
                   FROM {} ip
                   JOIN product_template pt
                     ON (SPLIT_PART(ip.res_id, ',', 2)::integer) = pt.id
                  WHERE ip.name = 'sla_id'
                    AND ip.value_reference LIKE 'helpdesk.sla,%'
                    AND ip.res_id LIKE 'product.template,%'
            """,
            "_ir_property" if util.version_gte("saas~17.5") else "ir_property",
        )
    )

    util.remove_field(cr, "helpdesk.sla", "sale_line_ids")
    util.remove_field(cr, "product.template", "sla_id")
    util.remove_view(cr, "helpdesk_sale_timesheet.product_template_form_view_invoice_policy_inherit_helpdesk")
