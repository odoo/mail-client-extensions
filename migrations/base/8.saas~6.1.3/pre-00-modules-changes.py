# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_module(cr, "base_report_designer")
    util.remove_module(cr, "crm_mass_mailing")
    util.remove_module(cr, "crm_profiling")  # FIXME convert to a survey?
    util.remove_module(cr, "l10n_fr_rib")
    util.remove_module(cr, "marketing_crm")
    util.remove_module(cr, "web_graph")
    util.remove_module(cr, "website_instantclick")
    util.remove_module(cr, "website_less")

    util.rename_module(cr, "portal_claim", "website_crm_claim")
    util.new_module_dep(cr, "website_crm_claim", "website")
    util.rename_module(cr, "portal_project_issue", "website_project_issue")
    util.new_module_dep(cr, "website_project_issue", "website")

    util.remove_module_deps(cr, "mass_mailing", ("web_kanban_sparkline",))
    util.remove_module_deps(cr, "sales_team", ("web_kanban_sparkline",))

    util.remove_module_deps(cr, "project_timesheet", ("hr_timesheet_sheet",))
    util.new_module_dep(cr, "project_timesheet", "hr_timesheet")

    util.remove_module_deps(cr, "account_asset", ("account",))
    util.new_module_dep(cr, "account_asset", "account_accountant")

    util.new_module(cr, "account_bank_statement_import")
    util.new_module_dep(cr, "account_bank_statement_import", "account")
    util.new_module(cr, "account_bank_statement_import_ofx")
    util.new_module_dep(cr, "account_bank_statement_import_ofx", "account_bank_statement_import")
    util.new_module(cr, "account_bank_statement_import_qif")
    util.new_module_dep(cr, "account_bank_statement_import_qif", "account_bank_statement_import")
    util.new_module_dep(cr, "l10n_be_coda", "account_bank_statement_import")

    for m in "analytic event hr_holidays".split():
        util.new_module_dep(cr, m, "report")

    util.new_module(cr, "barcodes")
    util.new_module_dep(cr, "barcodes", "web")
    util.new_module_dep(cr, "point_of_sale", "barcodes")
    util.new_module_dep(cr, "stock", "barcodes")

    util.new_module(cr, "inter_company_rules", deps={"sale", "purchase", "sale_stock", "sale_order_dates"})

    util.new_module(cr, "payment_authorize", deps={"payment"})

    if util.module_installed(cr, "procurement_jit") and not util.module_installed(cr, "stock"):
        # procurement_jit was already useless without stock. Do not force stock installation
        cr.execute("UPDATE ir_module_module SET state='to remove' WHERE name='procurement_jit'")

    util.new_module_dep(cr, "procurement_jit", "stock")
    util.remove_module(cr, "procurement_jit_stock")

    util.new_module(cr, "rating")
    util.new_module_dep(cr, "rating", "mail")
    util.new_module_dep(cr, "im_livechat", "rating")
    util.new_module(cr, "rating_project", deps={"rating", "project"})
    util.new_module(cr, "rating_project_issue", deps={"rating_project", "project_issue"}, auto_install=True)
    util.new_module(cr, "website_rating_project_issue", deps={"website_project_issue", "rating_project_issue"})

    util.new_module(cr, "planner", deps=("web",), auto_install=True)
    util.new_module(cr, "planner_crm", deps=("planner", "crm"), auto_install=True)

    util.merge_module(cr, "email_template", "mail")

    util.new_module(cr, "stock_calendar", deps={"purchase", "resource"})

    util.new_module(cr, "theme_default")
    util.new_module_dep(cr, "theme_default", "website")
    util.new_module(cr, "theme_bootswatch")
    util.new_module_dep(cr, "theme_bootswatch", "website")
    if util.module_installed(cr, "website"):
        themes = tuple(
            """theme_amelia theme_cerulean theme_cosmo
                          theme_cyborg theme_flatly theme_journal
                          theme_readable theme_simplex theme_slate
                          theme_spacelab theme_united theme_yeti
        """.split()
        )
        cr.execute(
            """SELECT 1
                        FROM ir_ui_view v
                        JOIN ir_model_data d ON (d.model='ir.ui.view' AND v.id=d.res_id)
                       WHERE d.module='website'
                         AND d.name IN %s
                         AND v.active=true
                   """,
            [themes],
        )
        if cr.rowcount:
            util.force_install_module(cr, "theme_bootswatch")
            for t in themes:
                util.rename_xmlid(cr, "website." + t, "theme_bootswatch." + t)
                util.force_noupdate(cr, "theme_bootswatch." + t, False)

        else:
            for t in themes:
                util.remove_view(cr, "website." + t)

            # other themes installed?
            cr.execute(
                """
                WITH RECURSIVE cats (id) AS (
                    SELECT id
                      FROM ir_module_category
                     WHERE parent_id IS NULL
                       AND lower(name) in ('theme', 'themes')
                   UNION
                    SELECT m.id
                      FROM ir_module_category m
                      JOIN cats c ON (m.parent_id = c.id)
                )
                SELECT name, state
                  FROM ir_module_module
                 WHERE category_id IN (SELECT id FROM cats)
                   AND state IN %s

            """,
                [util._INSTALLED_MODULE_STATES],
            )
            if not cr.rowcount:
                util.force_install_module(cr, "theme_default")

    util.new_module(cr, "website_links")
    util.new_module_dep(cr, "mass_mailing", "website_links")

    util.new_module(cr, "web_tip")
    util.new_module_dep(cr, "web_tip", "web")
    for m in "account crm event hr project purchase website_quote".split():
        util.new_module_dep(cr, m, "web_tip")

    util.new_module(cr, "mail_tip", deps=("mail", "web_tip"), auto_install=True)

    util.new_module(cr, "utm")
    util.new_module_dep(cr, "utm", "marketing")
    for m in "crm hr_recruitment mass_mailing".split():
        util.new_module_dep(cr, m, "utm")

    # `utm` module need a migration script to steal models from `crm` module
    # you may think this is clever hack, but I'm just an asshole that want the
    # migration script to be in a specific file instead of a method above...
    util.force_migration_of_fresh_module(cr, "utm")

    util.new_module(cr, "website_event_questions", deps={"website_event"})
    util.new_module(cr, "website_portal")
    util.new_module_dep(cr, "website_portal", "sale")
    util.new_module_dep(cr, "website_portal", "website")

    util.new_module_dep(cr, "website_sale", "website_portal")
    util.new_module_dep(cr, "website_payment", "website_portal")

    util.new_module_dep(cr, "website_quote", "payment")
    util.new_module_dep(cr, "website_quote", "website_portal")

    util.new_module(cr, "website_crm_score", deps=("base", "sales_team", "marketing", "website_crm"))
    util.new_module(cr, "website_sale_digital", deps={"document", "website_sale"})
    util.new_module(cr, "website_sale_stock", deps={"website_sale", "sale_stock"}, auto_install=True)
    util.new_module(cr, "website_slides", deps={"website", "website_mail"})
    util.new_module(cr, "website_version", deps={"website", "marketing", "google_account", "mail"})

    # correctly set the "demo" flag
    cr.execute("UPDATE ir_module_module SET demo=(SELECT demo FROM ir_module_module WHERE name='base')")
