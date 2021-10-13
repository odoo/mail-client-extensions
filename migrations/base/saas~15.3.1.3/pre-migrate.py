# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "base.language.install", "lang")
    util.create_m2m(cr, "res_lang_install_rel", "base_language_install", "res_lang", "language_wizard_id", "lang_id")
    util.remove_field(cr, "base.language.install", "state")
