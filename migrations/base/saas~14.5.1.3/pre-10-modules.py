# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_module(cr, "website_mail_channel")

    util.remove_module(cr, "website_sale_blog")
    cr.execute("DROP TABLE IF EXISTS product_blogpost_rel")

    if util.has_enterprise():
        util.new_module(cr, "hr_appraisal_skills", deps={"hr_appraisal", "hr_skills"}, auto_install=True)
        util.new_module(cr, "event_social", deps={"event", "social"}, auto_install=True)

        util.module_deps_diff(cr, "l10n_co_edi", plus={"account_edi"}, minus={"account"})

    util.new_module(cr, "project_mail_plugin", deps={"project", "mail_plugin"}, auto_install=True)
    util.new_module(cr, "hr_holidays_attendance", deps={"hr_holidays", "hr_attendance"}, auto_install=True)
    util.new_module(cr, "mail_group", deps={"mail", "portal"})
    if util.table_exists(cr, "mail_channel"):
        # Install the new mail_group module if there's some "mail_channel" with "email_send=True" in the database
        cr.execute("SELECT 1 FROM mail_channel WHERE email_send=TRUE FETCH FIRST ROW ONLY")
        if cr.rowcount:
            util.force_install_module(cr, "mail_group")
            util.force_migration_of_fresh_module(cr, "mail_group")
    util.new_module(cr, "website_mail_group", deps={"mail_group", "website"}, auto_install=True)

    util.merge_module(cr, "website_form", "website")
    util.module_deps_diff(cr, "website", plus={"mail", "google_recaptcha"})
