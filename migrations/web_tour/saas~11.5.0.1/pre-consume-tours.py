# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    all_tours = {
        "account": {"account_tour"},
        "crm": {"crm_tour"},
        "hr_expense": {"hr_expense_tour"},
        "hr_recruitment": {"hr_recruitment_tour"},
        "mail": {"mail_tour"},
        "portal": {"portal_load_homepage"},
        "point_of_sale": {"point_of_sale_tour"},
        "project": {"project_tour"},
        "sale": {"sale_tour"},
        "sale_management": {"sale_product_configurator_advanced_tour", "sale_product_configurator_tour"},
        "stock": {"stock"},
        "survey": {"test_survey"},
        "web_editor": {"rte", "rte_inline"},
        "website": {"banner", "contact", "theme_customize", "rte_translator"},
        "website_blog": {"blog"},
        "website_crm": {"website_crm_tour"},
        "website_event": {"event"},
        "website_event_sale": {"event_buy_tickets"},
        "website_forum": {"question", "forum_question"},
        "website_hr_recruitment": {"website_hr_recruitment_tour"},
        "website_sale": {"shop_custom_attribute_value", "shop", "shop_customize"},
        "website_sale_wishlist": {"shop_wishlist"},
        # enterprise tours
        "account_accountant": {"account_reports_widgets", "account_accountant_tour"},
        "documents": {"documents_tour"},
        "helpdesk": {"helpdesk_tour"},
        "project_timesheet": {"activity_creation", "test_screen_navigation"},
        "sale_subscription": {"sale_subscription_tour"},
        "timesheet_grid": {"timesheet_tour"},
        "web_studio": {
            "web_studio_home_menu_background_tour",
            "web_studio_new_app_tour",
            "web_studio_tests_tour",
            "web_studio_new_report_tour",
        },
        "website_form_editor": {
            "website_form_editor_tour",
            "website_form_editor_tour_submit",
            "website_form_editor_tour_results",
        },
        "website_sale_coupon": {"shop_sale_coupon"},
    }

    tours = set()
    for mod in all_tours:
        if util.module_installed(cr, mod):
            tours |= all_tours[mod]

    cr.execute(
        """
        INSERT INTO web_tour_tour(user_id, name)
             SELECT uid, unnest(%s)
               FROM res_groups_users_rel
              WHERE gid = %s
    """,
        [list(tours), util.ref(cr, "base.group_erp_manager")],
    )
