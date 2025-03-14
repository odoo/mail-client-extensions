from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "website_sale_onboarding_payment_provider_state")
    util.remove_field(cr, "res.config.settings", "terms_url")
    cr.execute(
        """
        WITH tab AS (
          SELECT rel.product_template_id AS ptid,
                 min(tag.ribbon_id) AS rid
            FROM product_tag_product_template_rel rel
            JOIN product_tag tag
              ON tag.id = rel.product_tag_id
           WHERE tag.ribbon_id IS NOT NULL
        GROUP BY rel.product_template_id
        )
        UPDATE product_template pt
           SET website_ribbon_id = tab.rid
          FROM tab
         WHERE tab.ptid = pt.id
           AND pt.website_ribbon_id IS NULL
        """
    )
    util.remove_field(cr, "product.tag", "ribbon_id")
    util.remove_field(cr, "product.ribbon", "product_tag_ids")

    util.remove_view(cr, "website_sale.res_config_settings_view_form_web_terms")
