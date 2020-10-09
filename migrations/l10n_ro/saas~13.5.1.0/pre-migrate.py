# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util

tax_report_convertor = util.import_script('account/0.0.0/end-tax-report-conversion.py')

def migrate(cr, version):
    tax_report_convertor.init_tax_report_conversion(cr, 'l10n_ro', [
        ('account_tax_report_baza_tva_0', 'account_tax_report_ro_baza_rd14'),
        ('account_tax_report_baza_tva_5', 'account_tax_report_ro_baza_rd111'),
        ('account_tax_report_tva_5', 'account_tax_report_ro_tva_rd111'),
        ('account_tax_report_baza_tva_9', 'account_tax_report_ro_baza_rd101'),
        ('account_tax_report_tva_9', 'account_tax_report_ro_tva_rd101'),
        ('account_tax_report_baza_tva_19', 'account_tax_report_ro_baza_rd91'),
        ('account_tax_report_tva_19', 'account_tax_report_ro_tva_rd91'),
        ('account_tax_report_baza_tva_deducbl_0', 'account_tax_report_ro_baza_rd30'),
        ('account_tax_report_baza_tva_deducbl_5', 'account_tax_report_ro_baza_rd261'),
        ('account_tax_report_ro_tva_decucible_5', 'account_tax_report_ro_tva_rd261'),
        ('account_tax_report_baza_tva_deducbl_9', 'account_tax_report_ro_baza_rd251'),
        ('account_tax_report_ro_tva_decucible_9', 'account_tax_report_ro_tva_rd251'),
        ('account_tax_report_baza_tva_deducbl_19', 'account_tax_report_ro_baza_rd241'),
        ('account_tax_report_ro_tva_decucible_19', 'account_tax_report_ro_tva_rd241'),
        ('account_tax_report_ro_baza_tva_tx_scutita_vnzari', 'account_tax_report_ro_baza_rd14'),
        ('account_tax_report_baza_tva_tx_invrsa', 'account_tax_report_ro_baza_rd123'),
        ('account_tax_report_ro_baza_tva_tx_invrsa', 'account_tax_report_ro_baza_rd273'),
        ('account_tax_report_tva_tx_invrsa', 'account_tax_report_ro_tva_rd123'),
        ('account_tax_report_ro_tva_tx_invrsa', 'account_tax_report_ro_tva_rd272'),
        ('account_tax_report_ro_tva_intracmunitr_bunri', 'account_tax_report_ro_tva_rd20'),
        ('account_tax_report_ro_baza_tva_intracmunitr_bnuri', 'account_tax_report_ro_baza_rd5'),
        ('account_tax_report_baza_tva_intrcmtr_bnr', 'account_tax_report_ro_baza_rd20'),
        ('account_tax_report_tva_intracmunitr_bunri', 'account_tax_report_ro_tva_rd5'),
        ('account_tax_report_ro_baza_tva_tx_intracmutr_nempzbl_achzti', 'account_tax_report_ro_baza_rd30'),
    ])
