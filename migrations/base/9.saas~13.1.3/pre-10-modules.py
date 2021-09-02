# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.has_enterprise():
        util.new_module_dep(cr, "quality", "decimal_precision")
        util.remove_module_deps(cr, "website_sign", ("website",))

        util.new_module(cr, "mrp_barcode", deps=("mrp_workorder", "stock_barcode"))
        util.new_module(cr, "helpdesk", deps=("base_setup", "mail", "utm", "rating"))
        util.new_module(
            cr,
            "web_studio",
            deps={
                "base_action_rule",
                "base_import_module",
                "grid",
                "mail",
                "report",
                "web",
                "web_calendar",
                "web_editor",
                "web_gantt",
                "web_kanban",
            },
        )
        util.new_module(cr, "website_helpdesk", deps=("website_form_editor", "helpdesk", "website_portal"))
        util.new_module(cr, "website_helpdesk_form", deps=("website_helpdesk",))
        util.new_module(cr, "website_helpdesk_forum", deps=("website_forum", "website_helpdesk"), auto_install=True)
        util.new_module(cr, "website_helpdesk_livechat", deps=("helpdesk", "website_livechat"), auto_install=True)
        util.new_module(cr, "website_helpdesk_slides", deps=("website_helpdesk", "website_slides"), auto_install=True)

        util.move_field_to_module(
            cr, "account.financial.html.report", "tax_report", "account_tax_exigible_enterprise", "account_reports"
        )
        util.remove_module(cr, "account_tax_exigible_enterprise")

        if util.has_design_themes():
            # Theme changes
            util.new_module_dep(cr, "snippet_latest_posts", "theme_common")
            util.remove_module_deps(cr, "snippet_latest_posts", ("website",))

            for theme in "avantgarde graphene".split():
                util.remove_module_deps(cr, "theme_" + theme, ("snippet_latest_posts",))
                util.new_module(
                    cr,
                    "theme_" + theme + "_blog",
                    deps=("theme_" + theme, "website_blog", "snippet_latest_posts"),
                    auto_install=True,
                )

    util.ENVIRON["tax_exigible_intalled"] = util.module_installed(cr, "account_tax_exigible")
    # beside behavior has been moved to `account_tax_cash_basis` module, fields have been moved
    # to `account` module
    util.merge_module(cr, "account_tax_exigible", "account")

    util.new_module_dep(cr, "auth_ldap", "base_setup")
    util.module_deps_diff(cr, "base_gengo", plus={"base_setup"}, minus={"base"})
    util.new_module_dep(cr, "hr_attendance", "barcodes")

    util.remove_module_deps(cr, "hr_recruitment", ("survey",))
    util.new_module(cr, "hr_recruitment_survey", deps=("hr_recruitment", "survey"), auto_install=True)

    util.remove_module_deps(cr, "hr_timesheet_sheet", ("hr_attendance",))
    util.new_module_dep(cr, "hr_timesheet_attendance", "hr_timesheet_sheet")
    util.remove_module_deps(cr, "hr_timesheet_attendance", ("hr_timesheet",))
    if util.module_installed(cr, "hr_timesheet_sheet"):
        # hr_timesheet_attendance was just a report. Now attendance logic is in this module.
        util.force_install_module(cr, "hr_timesheet_attendance")

    util.module_deps_diff(cr, "hr_payroll", minus={"hr"})

    util.new_module_dep(cr, "pad", "base_setup")

    util.new_module_dep(cr, "point_of_sale", "stock_account")
    util.remove_module_deps(cr, "point_of_sale", ("sale_stock",))

    util.merge_module(cr, "product_visible_discount", "sale")

    util.new_module_dep(cr, "report", "base_setup")

    util.remove_module_deps(cr, "subscription", ("sales_team",))

    # I hope anybody installed it...
    util.new_module_dep(cr, "test_new_api", "web_tour")

    # remove dead module
    util.remove_module(cr, "im_odoo_support")
    util.remove_module(cr, "report_webkit")
