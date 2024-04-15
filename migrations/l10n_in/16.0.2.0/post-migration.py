# -*- coding: utf-8 -*-


def migrate(cr, version):
    tag_map = {
        "tax_report_line_sgst": "tax_tag_sgst",
        "tax_report_line_cgst": "tax_tag_cgst",
        "tax_report_line_igst": "tax_tag_igst",
        "tax_report_line_cess": "tax_tag_cess",
        "tax_report_line_sgst_rc": "tax_tag_sgst_rc",
        "tax_report_line_cgst_rc": "tax_tag_cgst_rc",
        "tax_report_line_igst_rc": "tax_tag_igst_rc",
        "tax_report_line_cess_rc": "tax_tag_cess_rc",
        "tax_report_line_exempt": "tax_tag_exempt",
        "tax_report_line_nil_rated": "tax_tag_nill_rated",
        "tax_report_line_zero_rated": "tax_tag_zero_rated",
        "tax_report_line_non_gst_supplies": "tax_tag_non_gst_supplies",
        "tax_report_line_state_cess": "tax_tag_state_cess",
    }

    for tax_report_line, new_tax_tag in tag_map.items():
        # Add new tags in account.tax.repartition.line and remove old tag
        cr.execute(
            """
                INSERT INTO account_account_tag_account_tax_repartition_line_rel
                            (account_tax_repartition_line_id, account_account_tag_id)
                     SELECT rep_line_tag_rel.account_tax_repartition_line_id,
                            new_ir.res_id
                       FROM account_tax_report_line atrl
                       JOIN account_tax_report_line_tags_rel_backup report_tag_rel
                            ON report_tag_rel.account_tax_report_line_id = atrl.id
                       JOIN account_account_tag_account_tax_repartition_line_rel rep_line_tag_rel
                            ON rep_line_tag_rel.account_account_tag_id = report_tag_rel.account_account_tag_id
                       JOIN ir_model_data new_ir
                            ON new_ir.name = %s AND new_ir.model = 'account.account.tag'
                      WHERE atrl._upg_xmlid = %s
                        AND atrl._upg_module = 'l10n_in'
                    ON CONFLICT DO NOTHING
            """,
            (new_tax_tag, tax_report_line),
        )
        cr.execute(
            """
            DELETE FROM account_account_tag_account_tax_repartition_line_rel rep_line_tag_rel
                  USING account_tax_report_line atrl
                   JOIN account_tax_report_line_tags_rel_backup report_tag_rel
                        ON report_tag_rel.account_tax_report_line_id = atrl.id
                  WHERE atrl._upg_xmlid = %s
                    AND atrl._upg_module = 'l10n_in'
                    AND rep_line_tag_rel.account_account_tag_id = report_tag_rel.account_account_tag_id
            """,
            (tax_report_line,),
        )

        # Add new tags in account.move.line and remove old tag
        cr.execute(
            """
                INSERT INTO account_account_tag_account_move_line_rel
                            (account_move_line_id, account_account_tag_id)
                     SELECT move_tag_rel.account_move_line_id,
                            new_ir.res_id
                       FROM account_tax_report_line atrl
                       JOIN account_tax_report_line_tags_rel_backup report_tag_rel
                            ON report_tag_rel.account_tax_report_line_id = atrl.id
                       JOIN account_account_tag_account_move_line_rel move_tag_rel
                            ON move_tag_rel.account_account_tag_id = report_tag_rel.account_account_tag_id
                       JOIN ir_model_data new_ir
                            ON new_ir.name = %s AND new_ir.model = 'account.account.tag'
                      WHERE atrl._upg_xmlid = %s
                        AND atrl._upg_module = 'l10n_in'
                         ON CONFLICT DO NOTHING
            """,
            (new_tax_tag, tax_report_line),
        )
        cr.execute(
            """
                DELETE FROM account_account_tag_account_move_line_rel move_tag_rel
                      USING account_tax_report_line atrl
                       JOIN account_tax_report_line_tags_rel_backup report_tag_rel
                            ON report_tag_rel.account_tax_report_line_id = atrl.id
                      WHERE atrl._upg_xmlid = %s
                        AND atrl._upg_module = 'l10n_in'
                        AND move_tag_rel.account_account_tag_id = report_tag_rel.account_account_tag_id
            """,
            (tax_report_line,),
        )

    # Add base tags into account.tax.repartition.line
    tax_base_map = {
        "tax_tag_sgst": "tax_tag_base_sgst",
        "tax_tag_cgst": "tax_tag_base_cgst",
        "tax_tag_igst": "tax_tag_base_igst",
        "tax_tag_non_itc_sgst": "tax_tag_non_itc_base_sgst",
        "tax_tag_non_itc_cgst": "tax_tag_non_itc_base_cgst",
        "tax_tag_non_itc_igst": "tax_tag_non_itc_base_igst",
        "tax_tag_other_non_itc_sgst": "tax_tag_other_non_itc_base_sgst",
        "tax_tag_other_non_itc_cgst": "tax_tag_other_non_itc_base_cgst",
        "tax_tag_other_non_itc_igst": "tax_tag_other_non_itc_base_igst",
        "tax_tag_cess": "tax_tag_base_cess",
        "tax_tag_state_cess": "tax_tag_base_state_cess",
        "tax_tag_non_itc_cess": "tax_tag_non_itc_base_cess",
        "tax_tag_other_non_itc_cess": "tax_tag_other_non_itc_base_cess",
        "tax_tag_sgst_rc": "tax_tag_base_sgst_rc",
        "tax_tag_cgst_rc": "tax_tag_base_cgst_rc",
        "tax_tag_igst_rc": "tax_tag_base_igst_rc",
        "tax_tag_cess_rc": "tax_tag_base_cess_rc",
    }

    for tax_tag, base_tax_tag in tax_base_map.items():
        cr.execute(
            """
                INSERT INTO account_account_tag_account_tax_repartition_line_rel
                    (account_tax_repartition_line_id, account_account_tag_id)
                     SELECT COALESCE(invoice_rep_line_base.id, refund_rep_line_base.id),
                            base_tag.id
                       FROM account_account_tag_account_tax_repartition_line_rel repl_tag_rel
                       JOIN ir_model_data tag_ref
                            ON tag_ref.res_id = repl_tag_rel.account_account_tag_id
                            AND tag_ref.model = 'account.account.tag'
                            AND tag_ref.name = %s
                       JOIN account_tax_repartition_line rep_line
                            ON rep_line.id = repl_tag_rel.account_tax_repartition_line_id
                  LEFT JOIN account_tax_repartition_line invoice_rep_line_base
                            ON invoice_rep_line_base.invoice_tax_id = rep_line.invoice_tax_id
                            AND invoice_rep_line_base.repartition_type = 'base'
                  LEFT JOIN account_tax_repartition_line refund_rep_line_base
                            ON refund_rep_line_base.refund_tax_id = rep_line.refund_tax_id
                            AND refund_rep_line_base.repartition_type = 'base'
                       JOIN ir_model_data ref_base_tag
                            ON ref_base_tag.name = %s
                            AND ref_base_tag.model = 'account.account.tag'
                       JOIN account_account_tag base_tag
                            ON base_tag.id = ref_base_tag.res_id
                      WHERE invoice_rep_line_base.id IS NOT NULL OR refund_rep_line_base.id IS NOT NULL
                         ON CONFLICT DO NOTHING
            """,
            (tax_tag, base_tax_tag),
        )

    # Add base tags into account.move.line
    cr.execute(
        """
            WITH RECURSIVE child_tree(id, child_ids) AS (
                SELECT tax_fil_rel.parent_tax,
                       ARRAY_AGG(tax_fil_rel.child_tax)
                  FROM account_tax_filiation_rel tax_fil_rel
              GROUP BY tax_fil_rel.parent_tax
             UNION ALL
                SELECT tax_fil_rel.parent_tax, ARRAY_APPEND(ct.child_ids, tax_fil_rel.parent_tax)
                  FROM account_tax_filiation_rel tax_fil_rel
                  JOIN child_tree ct ON ct.id = tax_fil_rel.child_tax
            )
            INSERT INTO account_account_tag_account_move_line_rel
                (account_move_line_id, account_account_tag_id)
                 SELECT aml.id AS move_line_id,
                        CASE
                        WHEN am.move_type ILIKE '%_refund'
                        THEN refund_rpl_tag.account_account_tag_id
                        ELSE invoice_rpl_tag.account_account_tag_id
                        END AS base_tag_id
                   FROM account_move_line aml
                   JOIN account_move am
                        ON am.id = aml.move_id
                   JOIN account_move_line_account_tax_rel aml_tax
                        ON aml_tax.account_move_line_id = aml.id
              LEFT JOIN child_tree ct
                        ON ct.id = aml_tax.account_tax_id
                   JOIN account_tax_repartition_line invoice_rpl
                        ON (invoice_rpl.invoice_tax_id = aml_tax.account_tax_id
                        OR invoice_rpl.invoice_tax_id = ANY(ct.child_ids))
                        AND invoice_rpl.repartition_type = 'base'
                   JOIN account_account_tag_account_tax_repartition_line_rel invoice_rpl_tag
                        ON invoice_rpl_tag.account_tax_repartition_line_id = invoice_rpl.id
                   JOIN account_tax_repartition_line refund_rpl
                        ON (refund_rpl.refund_tax_id = aml_tax.account_tax_id
                        OR refund_rpl.refund_tax_id = ANY(ct.child_ids))
                        AND refund_rpl.repartition_type = 'base'
                   JOIN account_account_tag_account_tax_repartition_line_rel refund_rpl_tag
                        ON refund_rpl_tag.account_tax_repartition_line_id = refund_rpl.id
                  WHERE refund_rpl_tag.account_account_tag_id IS NOT NULL OR invoice_rpl_tag.account_account_tag_id IS NOT NULL
                ON CONFLICT DO NOTHING
        """
    )
