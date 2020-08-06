# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, 'account_tax_template', 'l10n_mx_tax_type', 'varchar', default='Tasa')
    util.create_column(cr, 'account_tax', 'l10n_mx_tax_type', 'varchar', default='Tasa')
