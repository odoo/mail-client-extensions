# -*- coding: utf-8 -*-
import psycopg2

from openerp.tools.misc import ignore

from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "l10n_be_intrastat_2019", deps=("l10n_be_intrastat",), auto_install=True)
    if util.has_enterprise():
        util.new_module(cr, "web_mobile", deps=("web_settings_dashboard",), auto_install=True)
        util.new_module(cr, "mail_push", deps=("mail", "web_mobile"), auto_install=True)
        util.new_module(cr, "sale_account_taxcloud", deps={"account_taxcloud", "sale"}, auto_install=True)
        util.new_module(cr, "stock_barcode_mobile", deps=("stock_barcode", "web_mobile"), auto_install=True)
        util.new_module(cr, "hr_expense_sepa", deps=("account_sepa", "hr_expense"), auto_install=True)
        util.new_module(
            cr, "website_sale_account_taxcloud", deps={"account_taxcloud", "website_sale"}, auto_install=True
        )
        util.new_module(
            cr,
            "website_sale_taxcloud_delivery",
            deps=("website_sale_delivery", "website_sale_account_taxcloud"),
            auto_install=True,
        )
        util.new_module_dep(cr, "web_studio", "portal")

    with ignore(psycopg2.Error), util.savepoint(cr):
        util.new_module(cr, "l10n_fr_certification", deps={"l10n_fr"})
        util.new_module(cr, "l10n_fr_sale_closing", deps={"l10n_fr_certification"}, auto_install=True)
        util.new_module(cr, "l10n_fr_pos_cert", deps={"l10n_fr_sale_closing", "point_of_sale"})
