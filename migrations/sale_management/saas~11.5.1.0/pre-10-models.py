# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_field(cr, "sale.order", "template_id", "sale_order_template_id")
    util.move_field_to_module(cr, "sale.order", "sale_order_template_id", "sale_quotation_builder", "sale_management")
    util.rename_field(cr, "sale.order", "options", "sale_order_option_ids")
    util.move_field_to_module(cr, "sale.order", "sale_order_option_ids", "sale_quotation_builder", "sale_management")
    util.move_field_to_module(cr, "sale.order", "require_payment", "sale_quotation_builder", "sale_management")
    cr.execute(
        """
        ALTER TABLE sale_order
        ALTER COLUMN require_payment
        TYPE boolean
        USING require_payment::boolean
    """
    )
    util.create_column(cr, "sale_order", "require_signature", "boolean")
    cr.execute(
        """
        UPDATE sale_order
        SET require_signature=TRUE
        WHERE require_payment=FALSE or require_payment IS NULL
    """
    )

    util.rename_field(cr, "sale.order.line", "option_line_id", "sale_order_option_ids")
    util.move_field_to_module(
        cr, "sale.order.line", "sale_order_option_ids", "sale_quotation_builder", "sale_management"
    )

    util.move_model(cr, "sale.order.option", "sale_quotation_builder", "sale_management")
    util.remove_field(cr, "sale.order.option", "layout_category_id")
    util.move_field_to_module(
        cr, "sale.order.option", "website_description", "sale_management", "sale_quotation_builder"
    )
    if util.module_installed(cr, "sale_quotation_builder"):
        util.rename_model(cr, *eb("sale.{quote,order}.template"))
        util.move_model(cr, "sale.order.template", "sale_quotation_builder", "sale_management")
        util.move_field_to_module(
            cr, "sale.order.template", "website_description", "sale_management", "sale_quotation_builder"
        )
        util.remove_field(cr, "sale.order.template", "quote_line")
        util.remove_field(cr, "sale.order.template", "options")
        cr.execute(
            """
            ALTER TABLE sale_order_template
            ALTER COLUMN require_payment
            TYPE boolean
            USING require_payment::boolean
        """
        )
        util.create_column(cr, "sale_order_template", "require_signature", "boolean")
        cr.execute(
            """
            UPDATE sale_order_template
            SET require_signature=TRUE
            WHERE require_payment=FALSE or require_payment IS NULL
        """
        )

        util.rename_model(cr, *eb("sale.{quote,order.template}.line"))
        util.move_model(cr, "sale.order.template.line", "sale_quotation_builder", "sale_management")
        util.rename_field(cr, "sale.order.template.line", "quote_id", "sale_order_template_id")
        util.move_field_to_module(
            cr, "sale.order.template.line", "website_description", "sale_management", "sale_quotation_builder"
        )
        util.create_column(cr, "sale_order_template_line", "display_type", "varchar")

        util.rename_model(cr, *eb("sale.{quote,order.template}.option"))
        util.move_model(cr, "sale.order.template.option", "sale_quotation_builder", "sale_management")
        util.rename_field(cr, "sale.order.template.option", "template_id", "sale_order_template_id")
        util.remove_field(cr, "sale.order.template.option", "layout_category_id")
        util.move_field_to_module(
            cr, "sale.order.template.option", "website_description", "sale_management", "sale_quotation_builder"
        )
