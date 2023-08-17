# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "product.report_simple_label")
    util.remove_view(cr, "product.report_productlabel")
    util.remove_view(cr, "product.report_simple_barcode")
    util.remove_view(cr, "product.report_productbarcode")
    util.remove_record(cr, "product.report_product_label")
    util.remove_record(cr, "product.report_product_product_barcode")
    util.remove_record(cr, "product.report_product_template_barcode")
    util.remove_view(cr, "product.report_producttemplatebarcode")

    util.remove_field(cr, "product.attribute", "is_used_on_products")
    util.update_field_usage(cr, "product.template", "lst_price", "list_price")
    util.remove_field(cr, "product.template", "lst_price")
    util.remove_record(cr, "product.product_attribute_value_action")

    util.rename_field(cr, "product.template", "type", "detailed_type", update_references=False)
    util.create_column(cr, "product_template", "type", "varchar")

    if util.module_installed(cr, "sale_purchase"):
        # recreate constraint since column was renamed
        cr.execute(
            r"""
            ALTER TABLE product_template
             DROP CONSTRAINT IF EXISTS product_template_service_to_purchase,
              ADD CONSTRAINT product_template_service_to_purchase
            CHECK (type != 'service' AND service_to_purchase != TRUE OR type = 'service')
            """
        )

    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            "UPDATE product_template SET type = detailed_type",
            table="product_template",
        ),
    )

    util.create_column(cr, "product_template_attribute_line", "value_count", "int4", default=0)

    cr.execute(
        """
        WITH attcount AS (
            SELECT product_template_attribute_line_id as id, count(*) as count
              FROM product_attribute_value_product_template_attribute_line_rel
          GROUP BY product_template_attribute_line_id
        )
        UPDATE product_template_attribute_line ptal
           SET value_count = a.count
          FROM attcount a
         WHERE a.id = ptal.id
    """
    )
