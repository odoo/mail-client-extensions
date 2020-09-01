# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Old tax report line xml ids and new tax report line xml ids
    tax_report_ref_map = {
        'tax_report_ta_vat_in': 'tax_report_input_tax_purchase_from_out_tax',
        'tax_report_tp_vat_in': 'tax_report_input_tax',
        'tax_report_ta_vat_out': 'tax_report_out_tax_sale',
        'tax_report_tp_vat_out': 'tax_report_out_tax',
        }
    if util.table_exists(cr, "l10n_th_new_tax_report_tag_map"):
        for old_ref, new_ref in tax_report_ref_map.items():
            # Update plus tags related to new tax report line
            cr.execute("""
                UPDATE l10n_th_new_tax_report_tag_map trm
                    SET new_plus_tag_id = tag.id,
                        new_tax_report_line_xml_ref = ir_md.name,
                        new_tax_report_line_id = atrl_tag.account_tax_report_line_id
                FROM account_tax_report_line_tags_rel atrl_tag
                JOIN ir_model_data ir_md ON res_id = atrl_tag.account_tax_report_line_id and model = 'account.tax.report.line'
                JOIN account_account_tag tag ON tag.id = atrl_tag.account_account_tag_id
                WHERE tag.tax_negate != true AND trm.old_tax_report_line_xml_ref = %s AND ir_md.name = %s
            """, (old_ref, new_ref)
            )

            # Update minus tags related to new tax report line
            cr.execute("""
                UPDATE l10n_th_new_tax_report_tag_map trm
                    SET new_minus_tag_id = tag.id,
                        new_tax_report_line_xml_ref = ir_md.name,
                        new_tax_report_line_id = atrl_tag.account_tax_report_line_id
                FROM account_tax_report_line_tags_rel atrl_tag
                JOIN ir_model_data ir_md ON res_id = atrl_tag.account_tax_report_line_id and model = 'account.tax.report.line'
                JOIN account_account_tag tag ON tag.id = atrl_tag.account_account_tag_id
                WHERE tag.tax_negate = true AND trm.old_tax_report_line_xml_ref = %s AND ir_md.name = %s
            """, (old_ref, new_ref)
            )

        # Update tag_ids in account.move.line
        cr.execute("""
            UPDATE account_account_tag_account_move_line_rel aml_tag
                SET account_account_tag_id = CASE
                  WHEN aml_tag.account_account_tag_id = tag_map.old_plus_tag_id THEN tag_map.new_plus_tag_id
                  ELSE tag_map.new_minus_tag_id END
                FROM l10n_th_new_tax_report_tag_map tag_map
                WHERE (aml_tag.account_account_tag_id = tag_map.old_plus_tag_id AND tag_map.new_plus_tag_id IS NOT NULL)
                  OR (aml_tag.account_account_tag_id = tag_map.old_minus_tag_id AND tag_map.new_minus_tag_id IS NOT NULL)
        """
        )

        # Update tag_ids in account.tax.repartition.line
        cr.execute("""
            UPDATE account_account_tag_account_tax_repartition_line_rel atrl_tag
                SET account_account_tag_id = CASE
                  WHEN atrl_tag.account_account_tag_id = tag_map.old_plus_tag_id THEN tag_map.new_plus_tag_id
                  ELSE tag_map.new_minus_tag_id END
                FROM l10n_th_new_tax_report_tag_map tag_map
                WHERE (atrl_tag.account_account_tag_id = tag_map.old_plus_tag_id AND tag_map.new_plus_tag_id IS NOT NULL)
                  OR (atrl_tag.account_account_tag_id = tag_map.old_minus_tag_id AND tag_map.new_minus_tag_id IS NOT NULL)
        """
        )

        # Remove unused tags
        cr.execute("""
            DELETE FROM account_account_tag aat USING l10n_th_new_tax_report_tag_map tag_map
            WHERE (aat.id = tag_map.old_plus_tag_id AND tag_map.new_plus_tag_id IS NOT NULL)
              OR (aat.id = tag_map.old_minus_tag_id AND tag_map.new_minus_tag_id IS NOT NULL)
        """
        )
        # Remove temporary map table
        cr.execute("DROP TABLE l10n_th_new_tax_report_tag_map")
