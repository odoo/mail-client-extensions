# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "mass_mailing_themes.theme_newsletter_template", noupdate=True)
