from psycopg2.extras import Json

from odoo.upgrade import util


def migrate(cr, version):
    """
    Some repartition lines have tags with inverted signs, leading to a whole section of the Austrian tax report having the wrong sign
    This script swaps the tag id in the account_account_tag_account_tax_repartition_line_rel table, so base repartition lines with
    the negative tags for document type invoice will now have the positive tag, and vice versa for the refund. Then, the same is
    done with the relation between account move lines and tags.
    """
    # Migration report messages
    message_repartition_lines = ""
    message_move_lines = ""
    message_adjustments = ""

    # Get the id of the tags applied incorrectly
    cr.execute(
        """
        SELECT tag.id
          FROM account_account_tag tag
          JOIN res_country country
            ON country.id = tag.country_id
         WHERE tag.name->>'en_US' ~ '[+-](KZ 008 Bemessungsgrundlage|KZ 070|KZ 071|KZ 072 Bemessungsgrundlage|KZ 073 Bemessungsgrundlage|KZ 076|KZ 077|KZ 088 Bemessungsgrundlage)$'
           AND country.code = 'AT'
        """
    )
    tag_ids = [tid for (tid,) in cr.fetchall()]

    # Get the positive and negative ids of tags for mapping
    cr.execute(
        """
        SELECT SUBSTRING(tag.name->>'en_US', 2) AS tag_name,
               MAX(tag.id) FILTER (WHERE tag.tax_negate = FALSE) AS positive_tag_id,
               MAX(tag.id) FILTER (WHERE tag.tax_negate = TRUE) AS negative_tag_id
          FROM account_account_tag tag
         WHERE tag.id = ANY(%s)
      GROUP BY tag_name
        """,
        [tag_ids],
    )
    tag_mapping = Json({tag[0]: {"positive": tag[1], "negative": tag[2]} for tag in cr.fetchall()})

    # Update the relation table between tags and repartition lines
    cr.execute(
        """
        -- Get the repartition line ids that have the wrong tags, where refund lines have positive tags and invoice lines have negative tags
        WITH tax_repartition_lines_with_inverted_tags AS (
            SELECT repartition_line.id,
                   repartition_line.document_type
              FROM account_tax_repartition_line repartition_line
              JOIN account_account_tag_account_tax_repartition_line_rel rel
                ON repartition_line.id = rel.account_tax_repartition_line_id
              JOIN account_account_tag tag
                ON tag.id = rel.account_account_tag_id
             WHERE repartition_line.repartition_type = 'base'
               AND tag.id = ANY(%(tag_ids)s)
               AND (
                   tag.tax_negate IS NOT True AND repartition_line.document_type = 'refund'
                   OR tag.tax_negate AND repartition_line.document_type = 'invoice'
               )
          GROUP BY repartition_line.id
        )
        UPDATE account_account_tag_account_tax_repartition_line_rel rel
           SET account_account_tag_id = COALESCE(
               CASE
                    WHEN inv.document_type = 'invoice'
                    THEN (%(tag_mapping)s::jsonb->(SUBSTRING(tag.name->>'en_US', 2))->>'positive')::int4
                    WHEN inv.document_type = 'refund'
                    THEN (%(tag_mapping)s::jsonb->(SUBSTRING(tag.name->>'en_US', 2))->>'negative')::int4
               END,
               rel.account_account_tag_id
           )
          FROM account_account_tag tag,
               tax_repartition_lines_with_inverted_tags inv
         WHERE tag.id = rel.account_account_tag_id
           AND inv.id = rel.account_tax_repartition_line_id
           AND tag.id = ANY(%(tag_ids)s)
     RETURNING rel.account_tax_repartition_line_id
        """,
        {"tag_ids": tag_ids, "tag_mapping": tag_mapping},
    )

    # Add summary of changes to the migration report
    updated_repartition_line_ids = [lid for (lid,) in cr.fetchall()]
    if updated_repartition_line_ids:
        cr.execute(
            """
            SELECT account_tax.id,
                   account_tax.name ->> 'en_US'
              FROM account_tax_repartition_line repartition_line
         LEFT JOIN account_tax
                ON repartition_line.tax_id = account_tax.id
             WHERE repartition_line.id = ANY(%s)
          GROUP BY account_tax.id
          ORDER BY account_tax.id
        """,
            [updated_repartition_line_ids],
        )
        updated_tax_ids = cr.fetchall()
        updated_taxes = " ".join(
            f"<li>{util.get_anchor_link_to_record('account.tax', tax_id, tax_name)}</li>"
            for tax_id, tax_name in updated_tax_ids
        )
        message_repartition_lines = f"""
            <h4>Updated taxes</h4>
            <ul>{updated_taxes}</ul>
        """

        updated_tax_ids = [tax[0] for tax in updated_tax_ids]
        # It's also necessary to update the relation between account move lines and tags
        cr.execute(
            """
            WITH aml_with_inverted_tags AS (
                SELECT aml.id,
                       account_move.move_type
                  FROM account_move_line aml
                  JOIN account_move
                    ON aml.move_id = account_move.id
                  JOIN account_account_tag_account_move_line_rel tag_aml_rel
                    ON aml.id = tag_aml_rel.account_move_line_id
                  JOIN account_account_tag tag
                    ON tag.id = tag_aml_rel.account_account_tag_id
                  JOIN account_move_line_account_tax_rel aml_tax_rel
                    ON aml.id = aml_tax_rel.account_move_line_id
                 WHERE tag.id = ANY(%(tag_ids)s)
                   AND (
                        tag.tax_negate IS NOT True AND account_move.move_type = 'in_refund'
                        OR tag.tax_negate AND account_move.move_type = 'in_invoice'
                   )
                   AND aml_tax_rel.account_tax_id = ANY(%(updated_tax_ids)s)
              GROUP BY aml.id, account_move.move_type
            ),
            _upd AS (
                UPDATE account_account_tag_account_move_line_rel rel
                   SET account_account_tag_id = COALESCE(
                       CASE
                            WHEN inv.move_type = 'in_invoice'
                            THEN (%(tag_mapping)s::jsonb->(SUBSTRING(tag.name->>'en_US', 2))->>'positive')::int4
                            WHEN inv.move_type = 'in_refund'
                            THEN (%(tag_mapping)s::jsonb->(SUBSTRING(tag.name->>'en_US', 2))->>'negative')::int4
                       END,
                       rel.account_account_tag_id
                   )
                  FROM account_account_tag tag,
                       aml_with_inverted_tags inv
                 WHERE tag.id = rel.account_account_tag_id
                   AND inv.id = rel.account_move_line_id
                   AND tag.id = ANY(%(tag_ids)s)
             RETURNING rel.account_move_line_id
            ) SELECT am.id,
                     am.name
                FROM _upd
                JOIN account_move_line aml
                  ON _upd.account_move_line_id = aml.id
                JOIN account_move am
                  ON am.id = aml.move_id
            GROUP BY am.id
            ORDER BY am.id
            """,
            {"tag_ids": tag_ids, "updated_tax_ids": updated_tax_ids, "tag_mapping": tag_mapping},
        )

        total_am_ids = cr.rowcount
        updated_am_ids = cr.fetchmany(50)
        if updated_am_ids:
            updated_moves = " ".join(
                f"<li>{util.get_anchor_link_to_record('account.move', move_id, move_name)}</li>"
                for move_id, move_name in updated_am_ids
            )

            message_move_lines = f"""
                <h4>Updated moves</h4>
                <p>
                    Tax tags were also updated in move lines to reflect the changes made to the repartition lines.
                    {total_am_ids} moves have updated lines{" (only the first 50 are shown)" if total_am_ids > 50 else ""}.
                </p>
                <ul>{updated_moves}</ul>
            """

        # Identify adjustments (misc entries with tags) that contain updated tags. Those are not changed, but should be checked.
        cr.execute(
            """
            SELECT am.id,
                   am.name
              FROM account_move_line aml
              JOIN account_move am
                ON aml.move_id = am.id
              JOIN account_account_tag_account_move_line_rel tag_aml_rel
                ON aml.id = tag_aml_rel.account_move_line_id
              JOIN account_account_tag tag
                ON tag.id = tag_aml_rel.account_account_tag_id
             WHERE tag.id = ANY(%s)
               AND am.move_type = 'entry'
          GROUP BY am.id
          ORDER BY am.id
        """,
            [tag_ids],
        )

        adjustment_ids = cr.fetchall()
        if adjustment_ids:
            adjustments = " ".join(
                f"<li>{util.get_anchor_link_to_record('account.move', move_id, move_name)}</li>"
                for move_id, move_name in adjustment_ids
            )

            message_adjustments = f"""
                <h4>Adjustments to check</h4>
                <p>These adjustments were not changed, but they use the updated tags. Please check these entries.</p>
                <ul>{adjustments}</ul>
            """

    if message_move_lines or message_repartition_lines:
        util.add_to_migration_reports(
            category="Tax Tags (Austria)",
            message=f"""
                 <details>
                    <summary>
                        Your database contains Austrian taxes that had inverted tags in the repartition lines. This caused
                        a section of the Austrian Tax Report to have the wrong sign, although the amounts were correct. If
                        you didn't manually change the tag in these taxes before, this upgrade will ensure that the tax
                        tags are changed in the required repartition lines. As a result, your Austrian tax report will be
                        unchanged, except for the sign of some amounts which were incorrect.
                        <br/>
                        Please check the amounts in your tax report.
                    </summary>
                    {message_repartition_lines}
                    {message_move_lines}
                    {message_adjustments}
                </details>
            """,
            format="html",
        )

    # Remove obsolete report lines to avoid duplicates/conflicts when updating XML
    older_records = [
        "l10n_at.tax_report_line_l10n_at_tva_line_4_14_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_15_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_16_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_17_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_18_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_19_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_14_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_15_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_16_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_17_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_18_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_19_tax",
        "l10n_at.tax_report_line_at_base_title_umsatz_base_4_14_19",
        "l10n_at.tax_report_line_at_tax_title_4_14_19",
        "l10n_at.tax_report_line_at_base_title_umsatz_base_4_28_31",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_28_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_29_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_30_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_31_base",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_28_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_29_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_30_tax",
        "l10n_at.tax_report_line_l10n_at_tva_line_4_31_tax",
        "l10n_at.tax_report_line_at_tax_title_4_28_31",
        "l10n_at.tax_report_line_l10n_at_tva_line_5_13_tag",
    ]
    for xid in older_records:
        util.remove_record(cr, xid)
