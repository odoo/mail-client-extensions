# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_latam_invoice_document.external_layout_{clean,bold}"))
    util.rename_xmlid(cr, *eb("l10n_latam_invoice_document.external_layout_{background,striped}"))
