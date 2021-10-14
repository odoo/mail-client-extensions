# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mass_mailing_themes.theme_airmail_template")
    util.remove_view(cr, "mass_mailing_themes.theme_resto_template")
    util.remove_view(cr, "mass_mailing_themes.theme_expo_template")
