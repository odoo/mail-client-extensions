# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.table_exists(cr, "tax_accounts_v12_bckp"):
        return

    # All the tags defined in l10n_es are financial
    cr.execute("""
        INSERT INTO v12_financial_tags_registry(tag_id)
        SELECT res_id
        FROM ir_model_data
        WHERE ir_model_data.module = 'l10n_es'
            AND ir_model_data.model = 'account.account.tag'
    """)

    # Define mapping for financial tags
    cr.execute("""
        INSERT INTO financial_tags_conversion_map (old_tag_name, new_tag_name, invoice_type, repartition_type, module)
        VALUES
        ('mod_115_02_03', 'mod_115_02', 'invoice', 'base', 'l10n_es'),
        ('mod_115_02_03', 'mod_115_02', 'refund', 'base', 'l10n_es'),
        ('mod_115_02_03', 'mod_115_03', 'invoice', 'tax', 'l10n_es'),
        ('mod_115_02_03', 'mod_115_03', 'refund', 'tax', 'l10n_es'),

        ('mod_303_01_03', 'mod_303_01', 'invoice', 'base', 'l10n_es'),
        ('mod_303_01_03', 'mod_303_01', 'refund', 'base', 'l10n_es'),
        ('mod_303_01_03', 'mod_303_03', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_01_03', 'mod_303_03', 'refund', 'tax', 'l10n_es'),

        ('mod_303_04_06', 'mod_303_04', 'invoice', 'base', 'l10n_es'),
        ('mod_303_04_06', 'mod_303_04', 'refund', 'base', 'l10n_es'),
        ('mod_303_04_06', 'mod_303_06', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_04_06', 'mod_303_06', 'refund', 'tax', 'l10n_es'),

        ('mod_303_07_09', 'mod_303_07', 'invoice', 'base', 'l10n_es'),
        ('mod_303_07_09', 'mod_303_07', 'refund', 'base', 'l10n_es'),
        ('mod_303_07_09', 'mod_303_09', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_07_09', 'mod_303_09', 'refund', 'tax', 'l10n_es'),

        ('mod_303_10_11', 'mod_303_10', 'invoice', 'base', 'l10n_es'),
        ('mod_303_10_11', 'mod_303_10', 'refund', 'base', 'l10n_es'),
        ('mod_303_10_11', 'mod_303_11', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_10_11', 'mod_303_11', 'refund', 'tax', 'l10n_es'),

        ('mod_303_12_13', 'mod_303_12', 'invoice', 'base', 'l10n_es'),
        ('mod_303_12_13', 'mod_303_12', 'refund', 'base', 'l10n_es'),
        ('mod_303_12_13', 'mod_303_13', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_12_13', 'mod_303_13', 'refund', 'tax', 'l10n_es'),

        ('mod_303_12_13', 'mod_303_12', 'invoice', 'base', 'l10n_es'),
        ('mod_303_12_13', 'mod_303_12', 'refund', 'base', 'l10n_es'),
        ('mod_303_12_13', 'mod_303_13', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_12_13', 'mod_303_13', 'refund', 'tax', 'l10n_es'),

        ('mod_303_14_15_sale', 'mod_303_14_sale', 'invoice', 'base', 'l10n_es'),
        ('mod_303_14_15_sale', 'mod_303_14_sale', 'refund', 'base', 'l10n_es'),
        ('mod_303_14_15_sale', 'mod_303_15', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_14_15_sale', 'mod_303_15', 'refund', 'tax', 'l10n_es'),

        ('mod_303_14_15_purchase', 'mod_303_14_purchase', 'invoice', 'base', 'l10n_es'),
        ('mod_303_14_15_purchase', 'mod_303_14_purchase', 'refund', 'base', 'l10n_es'),
        ('mod_303_14_15_purchase', 'mod_303_15', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_14_15_purchase', 'mod_303_15', 'refund', 'tax', 'l10n_es'),

        ('mod_303_16_18', 'mod_303_16', 'invoice', 'base', 'l10n_es'),
        ('mod_303_16_18', 'mod_303_16', 'refund', 'base', 'l10n_es'),
        ('mod_303_16_18', 'mod_303_18', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_16_18', 'mod_303_18', 'refund', 'tax', 'l10n_es'),

        ('mod_303_19_21', 'mod_303_19', 'invoice', 'base', 'l10n_es'),
        ('mod_303_19_21', 'mod_303_19', 'refund', 'base', 'l10n_es'),
        ('mod_303_19_21', 'mod_303_21', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_19_21', 'mod_303_21', 'refund', 'tax', 'l10n_es'),

        ('mod_303_22_24', 'mod_303_22', 'invoice', 'base', 'l10n_es'),
        ('mod_303_22_24', 'mod_303_22', 'refund', 'base', 'l10n_es'),
        ('mod_303_22_24', 'mod_303_24', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_22_24', 'mod_303_24', 'refund', 'tax', 'l10n_es'),

        ('mod_303_25_26', 'mod_303_25', 'invoice', 'base', 'l10n_es'),
        ('mod_303_25_26', 'mod_303_25', 'refund', 'base', 'l10n_es'),
        ('mod_303_25_26', 'mod_303_26', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_25_26', 'mod_303_26', 'refund', 'tax', 'l10n_es'),

        ('mod_303_28_29', 'mod_303_28', 'invoice', 'base', 'l10n_es'),
        ('mod_303_28_29', 'mod_303_28', 'refund', 'base', 'l10n_es'),
        ('mod_303_28_29', 'mod_303_29', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_28_29', 'mod_303_29', 'refund', 'tax', 'l10n_es'),

        ('mod_303_30_31', 'mod_303_30', 'invoice', 'base', 'l10n_es'),
        ('mod_303_30_31', 'mod_303_30', 'refund', 'base', 'l10n_es'),
        ('mod_303_30_31', 'mod_303_31', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_30_31', 'mod_303_31', 'refund', 'tax', 'l10n_es'),

        ('mod_303_32_33', 'mod_303_32', 'invoice', 'base', 'l10n_es'),
        ('mod_303_32_33', 'mod_303_32', 'refund', 'base', 'l10n_es'),
        ('mod_303_32_33', 'mod_303_33', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_32_33', 'mod_303_33', 'refund', 'tax', 'l10n_es'),

        ('mod_303_34_35', 'mod_303_34', 'invoice', 'base', 'l10n_es'),
        ('mod_303_34_35', 'mod_303_34', 'refund', 'base', 'l10n_es'),
        ('mod_303_34_35', 'mod_303_35', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_34_35', 'mod_303_35', 'refund', 'tax', 'l10n_es'),

        ('mod_303_36_37', 'mod_303_36', 'invoice', 'base', 'l10n_es'),
        ('mod_303_36_37', 'mod_303_36', 'refund', 'base', 'l10n_es'),
        ('mod_303_36_37', 'mod_303_37', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_36_37', 'mod_303_37', 'refund', 'tax', 'l10n_es'),

        ('mod_303_38_39', 'mod_303_38', 'invoice', 'base', 'l10n_es'),
        ('mod_303_38_39', 'mod_303_38', 'refund', 'base', 'l10n_es'),
        ('mod_303_38_39', 'mod_303_39', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_38_39', 'mod_303_39', 'refund', 'tax', 'l10n_es'),

        ('mod_303_40_41', 'mod_303_40', 'invoice', 'base', 'l10n_es'),
        ('mod_303_40_41', 'mod_303_40', 'refund', 'base', 'l10n_es'),
        ('mod_303_40_41', 'mod_303_41', 'invoice', 'tax', 'l10n_es'),
        ('mod_303_40_41', 'mod_303_41', 'refund', 'tax', 'l10n_es')
    """)

    # Some child taxes are not set as 'none' taxes; they should, in order to be merged in their parent
    cr.execute("""
        UPDATE account_tax
        SET type_tax_use = 'none'
        FROM ir_model_data
        WHERE ir_model_data.model = 'account.tax'
        AND ir_model_data.res_id = account_tax.id
        AND ir_model_data.module = 'l10n_es'
        AND ir_model_data.name like any (array['%account_tax_template_p_iva21_sp_in_1',
                                               '%account_tax_template_p_iva21_sp_in_2',
                                               '%account_tax_template_p_iva21_ic_bc_1',
                                               '%account_tax_template_p_iva21_ic_bc_2',
                                               '%account_tax_template_p_iva21_ic_bi_1',
                                               '%account_tax_template_p_iva21_ic_bi_2',
                                               '%account_tax_template_p_iva4_sp_ex_1',
                                               '%account_tax_template_p_iva4_sp_ex_2',
                                               '%account_tax_template_p_iva10_sp_ex_1',
                                               '%account_tax_template_p_iva10_sp_ex_2',
                                               '%account_tax_template_p_iva21_sp_ex_1',
                                               '%account_tax_template_p_iva21_sp_ex_2',
                                               '%account_tax_template_p_iva4_ic_bc_1',
                                               '%account_tax_template_p_iva4_ic_bc_2',
                                               '%account_tax_template_p_iva4_ic_bi_1',
                                               '%account_tax_template_p_iva4_ic_bi_2',
                                               '%account_tax_template_p_iva10_ic_bc_1',
                                               '%account_tax_template_p_iva10_ic_bc_2',
                                               '%account_tax_template_p_iva10_ic_bi_1',
                                               '%account_tax_template_p_iva10_ic_bi_2',
                                               '%account_tax_template_p_iva10_sp_in_1',
                                               '%account_tax_template_p_iva10_sp_in_2',
                                               '%account_tax_template_p_iva4_sp_in_1',
                                               '%account_tax_template_p_iva4_sp_in_2',
                                               '%account_tax_template_p_iva4_isp_1',
                                               '%account_tax_template_p_iva4_isp_2',
                                               '%account_tax_template_p_iva10_isp_1',
                                               '%account_tax_template_p_iva10_isp_2',
                                               '%account_tax_template_p_iva21_isp_1',
                                               '%account_tax_template_p_iva21_isp_2'])
    """)
