from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.create_column(cr, "uom_uom", "relative_factor", "float8")
    cr.execute(
        """
        UPDATE uom_uom
           SET relative_factor = 1.0 / factor
        """
    )

    util.create_column(cr, "uom_uom", "relative_uom_id", "int4")
    cr.execute(
        """
        UPDATE uom_uom uu
           SET relative_uom_id = ref.id
          FROM uom_uom ref
         WHERE uu.category_id = ref.category_id
           AND ref.uom_type = 'reference'
           AND ref.active IS TRUE
           AND uu.id != ref.id
        """
    )

    if util.module_installed(cr, "point_of_sale"):
        util.create_column(cr, "uom_uom", "is_pos_groupable", "boolean")
        cr.execute(
            """
            UPDATE uom_uom uu
               SET is_pos_groupable = uc.is_pos_groupable
              FROM uom_category uc
             WHERE uc.id = uu.category_id
            """
        )
    util.remove_model(cr, "uom.category")
    util.remove_field(cr, "uom.uom", "category_id")
    util.remove_field(cr, "uom.uom", "uom_type")
    util.remove_field(cr, "uom.uom", "factor_inv")
    util.remove_field(cr, "uom.uom", "ratio")
    util.remove_field(cr, "uom.uom", "color")
    util.remove_field(cr, "uom.uom", "rounding")

    util.rename_xmlid(cr, *eb("{product,uom}.decimal_product_uom"))
    cr.execute(
        "UPDATE decimal_precision SET name = 'Product Unit' WHERE id = %s", [util.ref(cr, "uom.decimal_product_uom")]
    )
    util.rename_xmlid(cr, *eb("uom.{,product_}uom_square_foot"))
    util.rename_xmlid(cr, *eb("uom.{,product_}uom_square_meter"))
    # this commit: 62faa32 can cause dup values
    uom_hour = util.ref(cr, "uom.product_uom_hour")
    if uom_hour is not None and uom_hour == util.ref(cr, "uom.product_uom_day"):
        uom_day = util.ensure_xmlid_match_record(cr, "uom.product_uom_day", "uom.uom", {"name": "Days"})
        if uom_day == uom_hour:
            cr.execute("DELETE FROM ir_model_data WHERE module = 'uom' AND name = 'product_uom_day'")
