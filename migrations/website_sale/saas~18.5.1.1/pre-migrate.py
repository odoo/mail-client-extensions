from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    util.create_column(cr, "website", "shop_opt_products_design_classes", "varchar")
    views_mapping = {
        "thumb_2_3": ["thumb_2_3"],
        "thumb_4_5": ["thumb_4_5"],
        "thumb_4_3": ["thumb_4_3"],
        "thumb_cover": ["thumb_cover"],
        "design_grid": ["design_grid"],
        "design_thumbs": ["design_thumbs"],
        "design_card": ["design_cards", "cc", "cc1"],
        "add_to_cart": ["has_cta"],
        "description": ["has_description"],
    }
    for website in env["website"].search([]):
        # Default classes:
        product_design_classes = ["actions_onhover", "img_secondary_show"]

        product_design_classes.append(
            "layout_list" if website.is_view_active("website_sale.products_list_view") else "layout_catalog"
        )

        # Removed templates
        for view, classnames in views_mapping.items():
            if website.is_view_active(f"website_sale.products_{view}"):
                product_design_classes.extend(classnames)

        classes = " ".join(f"o_wsale_products_opt_{o}" for o in product_design_classes)
        cr.execute(
            "UPDATE website SET shop_opt_products_design_classes = %s WHERE id = %s",
            [classes, website.id],
        )

    views_to_remove = [
        "card_group",
        "horizontal_card_2",
        "horizontal_card",
        "banner",
        "borderless_2",
        "borderless_1",
        "centered",
        "mini_name",
        "mini_price",
        "mini_image",
        "view_detail",
        "add_to_cart",
    ]

    for view in views_mapping:
        util.remove_view(cr, f"website_sale.products_{view}")
    for view in views_to_remove:
        util.remove_view(cr, f"website_sale.dynamic_filter_template_product_product_{view}")
