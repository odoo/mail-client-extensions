from odoo.upgrade import util


def migrate(cr, version):
    # Delete product_template Pricer view
    util.remove_view(cr, "pos_pricer.product_template_form_view_pricers")

    # Make pricer.tag.product_id point to a product instead of a product template
    # There must be only one tag per product, thus the template cannot have more than one product, otherwise it's invalid data
    cr.execute("ALTER TABLE pricer_tag DROP CONSTRAINT pricer_tag_product_id_fkey")
    util.explode_execute(
        cr,
        """
        UPDATE pricer_tag tag
           SET product_id = p.id
          FROM product_template t
          JOIN product_product p
            ON p.product_tmpl_id = t.id
         WHERE tag.product_id = t.id
        """,
        table="pricer_tag",
        alias="tag",
    )
    cr.execute("""
        ALTER TABLE pricer_tag
     ADD CONSTRAINT pricer_tag_product_id_fkey
        FOREIGN KEY (product_id) REFERENCES product_product(id)
          ON DELETE CASCADE
    """)

    # Move fields from product_template to product_product
    util.create_column(cr, "product_product", "pricer_store_id", "int4")
    util.create_column(cr, "product_product", "pricer_product_to_create_or_update", "bool")
    util.explode_execute(
        cr,
        """
        UPDATE product_product p
           SET pricer_store_id = t.pricer_store_id,
               pricer_product_to_create_or_update = t.pricer_product_to_create_or_update
          FROM product_template t
         WHERE p.product_tmpl_id = t.id
        """,
        table="product_product",
        alias="p",
    )

    # Delete product.template pricer related fields
    util.remove_field(cr, "product.template", "pricer_store_id", skip_inherit=("product.product",))
    util.remove_field(cr, "product.template", "pricer_product_to_create_or_update", skip_inherit=("product.product",))

    util.remove_field(cr, "product.template", "pricer_display_price", skip_inherit=("product.product",))
    util.remove_field(cr, "product.template", "pricer_tag_ids", skip_inherit=("product.product",))

    # Activate product variants
    util.update_record_from_xml(cr, "base.group_user", from_module="pos_pricer")
