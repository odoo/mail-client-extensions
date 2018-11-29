# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    #Enforce order of deletion
    util.remove_record(cr, 'l10n_ch.fiscal_position_tax_template_7')
    util.remove_record(cr, 'l10n_ch.fiscal_position_tax_template_8')
    util.remove_record(cr, 'l10n_ch.fiscal_position_tax_template_11')
    util.remove_record(cr, 'l10n_ch.fiscal_position_tax_template_12')
    util.remove_record(cr, 'l10n_ch.fiscal_position_tax_template_16')
    util.remove_record(cr, 'l10n_ch.fiscal_position_tax_template_18')

    util.remove_record(cr, 'l10n_ch.vat_38')
    util.remove_record(cr, 'l10n_ch.vat_38_incl')
    util.remove_record(cr, 'l10n_ch.vat_38_purchase')
    util.remove_record(cr, 'l10n_ch.vat_38_purchase_incl')
    util.remove_record(cr, 'l10n_ch.vat_38_invest')
    util.remove_record(cr, 'l10n_ch.vat_38_invest_incl')
    util.remove_record(cr, 'l10n_ch.vat_80')
    util.remove_record(cr, 'l10n_ch.vat_80_incl')
    util.remove_record(cr, 'l10n_ch.vat_80_purchase')
    util.remove_record(cr, 'l10n_ch.vat_80_purchase_incl')
    util.remove_record(cr, 'l10n_ch.vat_80_invest')
    util.remove_record(cr, 'l10n_ch.vat_80_invest_incl')

    # keep old tax groups and tags
    util.force_noupdate(cr, 'l10n_ch.tax_group_tva_38', True)
    util.force_noupdate(cr, 'l10n_ch.tax_group_tva_8', True)

    util.force_noupdate(cr, 'l10n_ch.vat_tag_301_a', True)
    util.force_noupdate(cr, 'l10n_ch.vat_tag_341_a', True)
    util.force_noupdate(cr, 'l10n_ch.vat_tag_301_b', True)
    util.force_noupdate(cr, 'l10n_ch.vat_tag_341_b', True)
