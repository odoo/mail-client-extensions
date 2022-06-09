# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "account_edi_ubl_cii", deps={"account_edi"}, auto_install=True)
    util.force_migration_of_fresh_module(cr, "account_edi_ubl_cii")

    util.rename_xmlid(cr, "l10n_be_edi.edi_efff_1", "account_edi_ubl_cii.edi_efff_1")
    util.rename_xmlid(cr, "l10n_nl_edi.edi_nlcius_1", "account_edi_ubl_cii.edi_nlcius_1")
    util.rename_xmlid(cr, "l10n_no_edi.edi_ehf_3", "account_edi_ubl_cii.edi_ehf_3")

    util.remove_module(cr, "l10n_be_edi")
    util.remove_module(cr, "l10n_nl_edi")
    util.remove_module(cr, "l10n_no_edi")

    util.merge_module(cr, "account_edi_ubl", "account_edi_ubl_cii")
    util.merge_module(cr, "account_edi_ubl_bis3", "account_edi_ubl_cii")
    util.merge_module(cr, "account_edi_facturx", "account_edi_ubl_cii")
