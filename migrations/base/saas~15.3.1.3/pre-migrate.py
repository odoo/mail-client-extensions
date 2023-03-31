# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "base.language.install", "lang")
    util.create_m2m(cr, "res_lang_install_rel", "base_language_install", "res_lang", "language_wizard_id", "lang_id")
    util.remove_field(cr, "base.language.install", "state")

    if util.module_installed(cr, "account"):
        util.move_field_to_module(cr, "res.partner", "credit_limit", "base", "account")
        util.make_field_company_dependent(cr, "res.partner", "credit_limit", "float")
    else:
        util.remove_field(cr, "res.partner", "credit_limit")
