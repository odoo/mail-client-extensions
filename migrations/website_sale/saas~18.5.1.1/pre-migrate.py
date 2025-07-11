from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    util.create_column(cr, "website", "shop_opt_products_design_classes", "varchar")
    util.create_column(cr, "website", "product_page_image_ratio", "varchar")

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

    product_page_carousel_ratio_mapping = {
        "products_carousel_4x3": "4_3",
        "products_carousel_4x5": "4_5",
        "products_carousel_16x9": "16_9",
        "products_carousel_21x9": "21_9",
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

        # Product Page - Carousel image ratio
        image_ratio = "1_1"  # Default value
        for template_name, ratio_value in product_page_carousel_ratio_mapping.items():
            if website.is_view_active(f"website_sale.{template_name}"):
                image_ratio = ratio_value
                break

        # Update both product design classes and aspect-ratio columns
        cr.execute(
            "UPDATE website SET shop_opt_products_design_classes = %s, product_page_image_ratio = %s WHERE id = %s",
            [classes, image_ratio, website.id],
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

    for template_name in product_page_carousel_ratio_mapping:
        util.remove_view(cr, f"website_sale.{template_name}")

    util.remove_view(cr, "website_sale.snippets_options_web_editor")
    util.remove_view(cr, "website_sale.variants_separator")
    util.remove_view(cr, "website_sale.shop_fullwidth")

    click_view = env.ref("website_sale.product_picture_magnify_click")
    cr.execute(
        r"""
        SELECT hover_view.website_id
          FROM ir_ui_view hover_view
     LEFT JOIN ir_ui_view other_magnify_view
            ON other_magnify_view.website_id IS NOT DISTINCT FROM hover_view.website_id
           AND other_magnify_view.key LIKE 'website\_sale.product\_picture\_magnify%'
           AND other_magnify_view.key != 'website_sale.product_picture_magnify_hover'
           AND other_magnify_view.active
         WHERE hover_view.key = 'website_sale.product_picture_magnify_hover'
           AND hover_view.active IS NOT TRUE
           AND other_magnify_view IS NULL
        """
    )

    for none_website_id in cr.fetchall():
        click_view.with_context(website_id=none_website_id[0]).active = False

    util.remove_view(cr, "website_sale.product_picture_magnify_hover")
    util.remove_view(cr, "website_sale.product_picture_magnify_both")

    cr.execute(
        """
        UPDATE ir_ui_view v
           SET active = True
          FROM ir_model_data d
         WHERE v.id = d.res_id
           AND d.module = 'website_sale'
           AND d.name = 'product_picture_magnify_click'
           AND v.active IS NOT TRUE
        """
    )
