# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "hr_org_chart", ("hr",))
    util.new_module(cr, "l10n_be_hr_payroll_fleet", ("l10n_be_hr_payroll", "fleet"), auto_install=True)
    util.new_module(cr, "mass_mailing_event", ("event", "mass_mailing"), auto_install=True)
    util.new_module(cr, "mass_mailing_event_track", ("mass_mailing", "website_event_track"), auto_install=True)
    util.new_module(cr, "website_portal_purchase", ("website_portal", "purchase"), auto_install=True)
    util.new_module(cr, "project_timesheet_holidays", ("hr_timesheet", "hr_holidays"), auto_install=True)
    util.new_module(cr, "phone_validation", ("base",))
    util.new_module(
        cr,
        "crm_phone_validation",
        ("phone_validation", "crm"),
    )
    util.new_module(
        cr, "website_crm_phone_validation", ("crm_phone_validation", "website_crm", "website_form"), auto_install=True
    )

    util.merge_module(cr, "portal_gamification", "gamification")
    util.remove_view(cr, "web_kanban.assets_backend")
    util.merge_module(cr, "web_kanban", "web")
    util.remove_view(cr, "web_calendar.assets_backend")
    util.merge_module(cr, "web_calendar", "web", update_dependers=False)

    util.remove_module_deps(cr, "account_bank_statement_import", ("account",))
    util.new_module_dep(cr, "account_bank_statement_import", "account_accountant")

    util.remove_module_deps(cr, "hr_payroll_account", ("hr_expense",))
    util.module_deps_diff(cr, "point_of_sale", plus={"web_editor"})

    util.new_module_dep(cr, "website_portal", "auth_signup")

    # portal modules
    # In v7, some mail.group (now mail.channel) have been created by portal module. Keep them.
    cr.execute(
        """
        DELETE FROM ir_model_data
         WHERE module = 'portal'
           AND model IN ('mail.alias', 'mail.channel')
    """
    )
    util.rename_xmlid(cr, "portal.demo_user0", "base.demo_user0")
    util.rename_xmlid(cr, "portal.partner_demo_portal", "base.partner_demo_portal")
    util.move_field_to_module(cr, "res.groups", "is_portal", "portal", "base")

    if util.module_installed(cr, "website_portal"):
        util.move_model(cr, "portal.wizard", "portal", "website_portal")
        util.move_model(cr, "portal.wizard.user", "portal", "website_portal")
        util.rename_xmlid(cr, *util.expand_braces("{,website_}portal.mail_template_data_portal_welcome"))

    util.remove_module(cr, "portal")

    # portal stock
    util.rename_xmlid(cr, "portal_stock.portal_stock_picking_portal_user_rule", "stock.stock_picking_rule_portal")
    util.rename_xmlid(
        cr, "portal_stock.portal_stock_pack_operation_portal_user_rule", "stock.stock_pack_operation_rule_portal"
    )
    util.remove_module(cr, "portal_stock")

    # respect exclude tag of l10n_fr
    if util.module_installed(cr, "l10n_fr"):
        cr.execute(
            """
            UPDATE ir_module_module
               SET state = CASE WHEN state IN ('installed', 'to upgrade') THEN 'to remove'
                                WHEN state = 'to install' THEN 'uninstalled'
                                ELSE state END
             WHERE name = 'account_cancel'
        """
        )

    if util.has_enterprise():
        util.new_module(cr, "sms", ("base", "mail"))
        util.new_module(cr, "sms_fortytwo", ("sms",), auto_install=True)
        util.new_module(cr, "calendar_sms", ("calendar", "sms"), auto_install=True)
        util.new_module(cr, "website_calendar", ("calendar_sms", "website", "hr"))
        util.new_module(
            cr,
            "hr_contract_salary",
            ("hr", "website", "hr_recruitment", "l10n_be_hr_payroll_fleet", "website_sign"),
            auto_install=True,
        )

        util.new_module(
            cr, "project_timesheet_forecast_sale", ("project_forecast", "sale_timesheet"), auto_install=True
        )

        util.rename_module(cr, "grid", "web_grid")

        util.remove_view(cr, "project_forecast_grid.project_kanban_forecast_grid_button")
        util.remove_view(cr, "project_forecast_grid.project_form_forecast_grid_button")
        util.merge_module(cr, "project_forecast_grid", "project_forecast")
        util.new_module_dep(cr, "project_forecast", "web_grid")
        util.new_module_dep(cr, "project_forecast", "hr")
        util.force_migration_of_fresh_module(cr, "project_timesheet_forecast_sale")
