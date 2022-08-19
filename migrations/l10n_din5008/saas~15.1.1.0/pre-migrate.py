# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    for model in {"account.move", "base.document.layout", "account.analytic.line"}:
        for suffix in {"template_data", "document_title"}:
            util.move_field_to_module(cr, model, f"l10n_de_{suffix}", *eb("l10n_{de,din5008}"))
            util.rename_field(cr, model, *eb(f"l10n_{{de,din5008}}_{suffix}"))

    util.rename_xmlid(cr, *eb("{l10n_de,l10n_din5008}.paperformat_euro_din"))
    util.rename_xmlid(cr, *eb("{l10n_de,l10n_din5008}.paperformat_euro_dina"))
    util.rename_xmlid(cr, *eb("{l10n_de,l10n_din5008}.din5008_css"))
    util.rename_xmlid(cr, *eb("{l10n_de,l10n_din5008}.external_layout_din5008"))
