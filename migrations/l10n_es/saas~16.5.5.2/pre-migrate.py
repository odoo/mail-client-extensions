# -*- coding: utf-8 -*-
from odoo.upgrade import util

tag_migration_utils = util.import_script("l10n_mn/saas~16.5.1.1/pre-migrate.py")


def migrate(cr, version):
    if util.module_installed(cr, "l10n_es_reports"):
        # Migrate expressions
        eb = util.expand_braces
        xml_ids = [
            "mod_303_casilla_43_balance",
            "mod_303_casilla_44_balance",
            "mod_303_casilla_62_balance",
            "mod_303_casilla_63_balance",
            "mod_303_casilla_65_balance",
            "mod_303_casilla_67_balance",
            "mod_303_casilla_68_balance",
            "mod_303_casilla_70_balance",
            "mod_303_casilla_109_balance",
            "mod_303_casilla_74_balance",
            "mod_303_casilla_75_balance",
            "mod_303_casilla_77_balance",
            "mod_303_casilla_78_balance",
            "mod_303_casilla_110_balance",
            "mod_115_casilla_04_balance",
            "mod_111_title_8_balance",
            "mod_111_casilla_13_balance",
            "mod_111_casilla_14_balance",
            "mod_111_casilla_15_balance",
            "mod_111_casilla_16_balance",
            "mod_111_casilla_17_balance",
            "mod_111_casilla_18_balance",
            "mod_111_casilla_19_balance",
            "mod_111_casilla_20_balance",
            "mod_111_casilla_21_balance",
            "mod_111_casilla_22_balance",
            "mod_111_casilla_23_balance",
            "mod_111_casilla_24_balance",
            "mod_111_casilla_25_balance",
            "mod_111_casilla_26_balance",
            "mod_111_casilla_27_balance",
            "mod_111_casilla_29_balance",
        ]

        for xml_id in xml_ids:
            util.rename_xmlid(cr, *eb("l10n_es{_reports,}." + xml_id))

    tag_migration_utils.disable_obsolete_tax_tag(cr, "l10n_es.mod_303_61")
