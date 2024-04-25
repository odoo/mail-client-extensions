from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id
          FROM ir_ui_view
         WHERE key = 'website_sale.product'
           AND website_id IS NOT NULL
           AND arch_db->>'en_US' ~ '\ypricelist=pricelist\y'
        """
    )
    for (view,) in cr.fetchall():
        with util.edit_view(cr, view_id=view) as arch:
            combination_info = arch.find('.//t[@t-set="combination_info"]')
            if combination_info is not None:
                combination_info.attrib.update(
                    {"t-value": "product._get_combination_info(combination, add_qty=add_qty)"}
                )
            product_detail = arch.find('.//section[@id="product_detail"]')
            if product_detail is not None:
                product_detail.attrib.update(
                    {
                        "t-att-data-product-tracking-info": "'product_tracking_info' in combination_info and json.dumps(combination_info['product_tracking_info'])"
                    }
                )
