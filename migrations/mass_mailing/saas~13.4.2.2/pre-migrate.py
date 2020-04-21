# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_xmlid(cr, *eb("{website_mass_mailing,mass_mailing}.social_links"), noupdate=False)
    util.create_column(cr, "mailing_mailing", "kpi_mail_required", "boolean")
