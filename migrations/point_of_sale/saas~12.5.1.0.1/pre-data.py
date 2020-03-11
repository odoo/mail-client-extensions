# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    consumable = "point_of_sale.product_product_consumable"
    consumable_tmpl = f"{consumable}_product_template"

    util.delete_unused(cr, consumable)
    if util.ref(cr, consumable):
        # if product still there, mark the template as noupdate
        util.force_noupdate(cr, consumable_tmpl, True)
    else:
        util.delete_unused(cr, consumable_tmpl)

    util.rename_xmlid(cr, *eb("point_of_sale.product_product_{consumable,misc}"))
    util.rename_xmlid(cr, *eb("point_of_sale.product_product_{consumable,misc}_product_template"))

    util.force_noupdate(cr, "point_of_sale.pos_sale_journal", True)

    records = util.splitlines(
        """
        action_account_journal_form
        menu_action_account_journal_form
        account_journal_action_point_of_sale
        action_report_account_statement
        act_pos_config_sessions
        pos_menu_products_variants_action
        act_pos_session_orders
        action_pos_box_in
        act_pos_open_statement
        action_pos_open_statement
    """
    )
    for rec in records:
        util.remove_record(cr, "point_of_sale." + rec)

    views = util.splitlines(
        """
        view_account_journal_search_inherit_point_of_sale
        view_account_journal_pos_user_form
        view_pos_open_statement

        wysiwyg_iframe_css_assets

        # QWeb templates
        extra_head
        pos_editor_assets
        customer_facing_display_snippets

        report_statement
    """
    )
    for view in views:
        util.remove_view(cr, "point_of_sale." + view)
