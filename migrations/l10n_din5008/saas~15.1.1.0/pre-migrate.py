# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.move_field_to_module(cr, "account.move", "l10n_de_template_data", *eb("l10n_{de,din5008}"))
    util.move_field_to_module(cr, "account.move", "l10n_de_document_title", *eb("l10n_{de,din5008}"))
    util.move_field_to_module(cr, "base.document.layout", "l10n_de_template_data", *eb("l10n_{de,din5008}"))
    util.move_field_to_module(cr, "base.document.layout", "l10n_de_document_title", *eb("l10n_{de,din5008}"))

    util.rename_field(cr, "account.move", *eb("l10n_{de,din5008}_template_data"))
    util.rename_field(cr, "account.move", *eb("l10n_{de,din5008}_document_title"))
    util.rename_field(cr, "base.document.layout", *eb("l10n_{de,din5008}_template_data"))
    util.rename_field(cr, "base.document.layout", *eb("l10n_{de,din5008}_document_title"))

    util.rename_xmlid(cr, *eb("{l10n_de,l10n_din5008}.paperformat_euro_din"))
    util.rename_xmlid(cr, *eb("{l10n_de,l10n_din5008}.paperformat_euro_dina"))
    util.rename_xmlid(cr, *eb("{l10n_de,l10n_din5008}.din5008_css"))
    util.rename_xmlid(cr, *eb("{l10n_de,l10n_din5008}.external_layout_din5008"))
