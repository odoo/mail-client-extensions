# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "mass_mailing_themes.email_designer_snippets", "mass_mailing_themes.email_designer_themes")
