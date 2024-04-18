from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "account.intrastat.report")
    util.remove_view(cr, "account_intrastat.search_template")
    util.remove_view(cr, "account_intrastat.view_intrastat_code_expiry_search")
    util.remove_view(cr, "account_intrastat.view_report_intrastat_code_expiry_tree")
    util.remove_view(cr, "account_intrastat.view_report_intrastat_code_expiry_form")
    util.remove_view(cr, "account_intrastat.invoice_form_inherit_account_intrastat_expiry")
    util.remove_view(cr, "account_intrastat.account_intrastat_expiry_product_category_search_view")
    util.remove_view(cr, "account_intrastat.account_intrastat_expiry_product_template_search_view")
    util.remove_view(cr, "account_intrastat.product_category_tree_view_account_intrastat_expiry")
    util.remove_view(cr, "account_intrastat.product_category_form_view_inherit_account_intrastat")
    util.rename_xmlid(
        cr,
        "account_intrastat.product_product_tree_view_account_intrastat_expiry",
        "account_intrastat.product_product_tree_view_account_intrastat",
    )
    util.rename_xmlid(
        cr,
        "account_intrastat.account_intrastat_expiry_main_template",
        "account_intrastat.account_intrastat_main_template",
    )

    # Delete the product template field intrastat_id field, and assign its value to empty child product variants on
    # the "intrastat_code_id" field. Update the origin country field on the variant with it's parent template's value.
    util.create_column(cr, "product_product", "intrastat_code_id", "int4")
    util.create_column(cr, "product_product", "intrastat_origin_country_id", "int4")

    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE product_product prod
               SET intrastat_code_id = COALESCE(prod.intrastat_variant_id, prodt.intrastat_id),
                   intrastat_origin_country_id = prodt.intrastat_origin_country_id
              FROM product_template prodt
             WHERE prod.product_tmpl_id = prodt.id
            """,
            table="product_product",
            alias="prod",
        ),
    )

    # Rename the intrastat code field on the product product
    # Remove the commodity code fields on the product template and product category
    util.remove_field(cr, "product.template", "intrastat_id")
    util.remove_column(cr, "product_template", "intrastat_origin_country_id")
    util.remove_field(cr, "product.category", "intrastat_id")
    util.remove_field(cr, "product.product", "intrastat_variant_id")
