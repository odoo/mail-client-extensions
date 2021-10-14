# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_field(cr, "purchase.order", *eb("l10n_{de,din5008}_template_data"))
    util.rename_field(cr, "purchase.order", *eb("l10n_{de,din5008}_document_title"))
    util.rename_field(cr, "purchase.order", *eb("l10n_{de,din5008}_addresses"))
