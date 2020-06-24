# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # 1. Models were moved from sale_coupon to coupon
    util.move_model(cr, "sale.coupon", "sale_coupon", "coupon", move_data=True)
    util.move_model(cr, "sale.coupon.program", "sale_coupon", "coupon", move_data=True)
    util.move_model(cr, "sale.coupon.rule", "sale_coupon", "coupon", move_data=True)
    util.move_model(cr, "sale.coupon.reward", "sale_coupon", "coupon", move_data=True)
    util.move_model(cr, "sale.coupon.generate", "sale_coupon", "coupon", move_data=True)
    # 2. Moved models were renamed
    util.rename_model(cr, "sale.coupon", "coupon.coupon")
    util.rename_model(cr, "sale.coupon.program", "coupon.program")
    util.rename_model(cr, "sale.coupon.rule", "coupon.rule")
    util.rename_model(cr, "sale.coupon.reward", "coupon.reward")
    util.rename_model(cr, "sale.coupon.generate", "coupon.generate.wizard")
    util.rename_model(cr, "report.sale_coupon.report_coupon", "report.coupon.report_coupon", rename_table=False)
    # 3. Views were renamed as well
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{sale_coupon,coupon}.mail_template_sale_coupon"))
    util.rename_xmlid(cr, *eb("{sale_coupon,coupon}.sale_coupon_generate_rule"))
    util.rename_xmlid(cr, *eb("{sale_coupon.sale_,coupon.}coupon_program_view_form_common"))
    util.rename_xmlid(cr, "sale_coupon.sale_coupon_program_view_form", "coupon.coupon_program_view_coupon_program_form")
    util.rename_xmlid(cr, *eb("{sale_coupon.sale_,coupon.}coupon_program_view_tree"))
    util.rename_xmlid(cr, *eb("{sale_coupon.sale_,coupon.}coupon_program_view_search"))
    util.rename_xmlid(cr, *eb("{sale_coupon.view_sale,coupon.view}_coupon_program_kanban"))
    util.rename_xmlid(cr, *eb("{sale_coupon.sale_,coupon.}coupon_program_action_coupon_program"))
    util.rename_xmlid(
        cr, *eb("{sale_coupon.sale_,coupon.}coupon_program_view_promo_program_form"),
    )
    util.rename_xmlid(
        cr, *eb("{sale_coupon.sale_,coupon.}coupon_program_view_promo_program_tree"),
    )
    util.rename_xmlid(
        cr, *eb("{sale_coupon.sale_coupon,coupon.coupon}_program_view_promo_program_search"),
    )
    util.rename_xmlid(cr, *eb("{sale_coupon.sale_,coupon.}coupon_program_action_promo_program"))
    util.rename_xmlid(cr, *eb("{sale_coupon.sale_,coupon.}coupon_view_tree"))
    util.rename_xmlid(cr, *eb("{sale_coupon.sale_,coupon.}coupon_action"))
    util.rename_xmlid(cr, *eb("{sale_coupon.sale_,coupon.}coupon_view_form"))
    util.rename_xmlid(cr, *eb("{sale_coupon.sale_,coupon.}coupon_generate_view_form"))
    util.rename_xmlid(cr, *eb("{sale_coupon.sale_,coupon.}coupon_generate_action"))
    util.rename_xmlid(cr, *eb("{sale_coupon,coupon}.expire_coupon_cron"))
    util.rename_xmlid(cr, *eb("{sale_coupon,coupon}.report_coupon"))
    util.rename_xmlid(cr, *eb("{sale_coupon,coupon}.report_coupon_i18n"))

    # 4. Some fields remained at sale_coupon module
    util.move_field_to_module(cr, "coupon.coupon", "order_id", "coupon", "sale_coupon")
    util.move_field_to_module(cr, "coupon.coupon", "sale_order_id", "coupon", "sale_coupon")
    util.move_field_to_module(cr, "coupon.program", "order_count", "coupon", "sale_coupon")
