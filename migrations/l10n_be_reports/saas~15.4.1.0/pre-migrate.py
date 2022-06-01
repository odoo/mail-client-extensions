# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "l10n_be_reports.periodic.vat.xml.export", "grid91")
