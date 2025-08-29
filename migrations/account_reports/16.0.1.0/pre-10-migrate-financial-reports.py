import os

from odoo.upgrade import util

ODOO_MIG_16_MIGRATE_CUSTOM_FINANCIAL_REPORTS = util.str2bool(
    os.getenv("ODOO_MIG_16_MIGRATE_CUSTOM_FINANCIAL_REPORTS"), ""
)


def migrate(cr, version):
    # get ids of custom financial reports
    cr.execute(
        r"""
        SELECT afhr.id, afhr.name
          FROM account_financial_html_report afhr
     LEFT JOIN ir_model_data imd
            ON imd.res_id = afhr.id
           AND imd.model = 'account.financial.html.report'
           AND imd.module NOT LIKE '\_\_%'  -- __{import,export}__
         WHERE imd IS NULL
        """
    )

    custom_fin_reports = cr.fetchall()

    if not custom_fin_reports:
        return  # nosemgrep: no-early-return

    if not (ODOO_MIG_16_MIGRATE_CUSTOM_FINANCIAL_REPORTS or util.on_CI()):
        util.add_to_migration_reports(
            """
                <details>
                    <summary>
                        Due to a complete revamp of the reporting engine in Odoo 16, custom financial reports are not migrated by
                        default.
                        The general suggestion is to try to fallback on the new capabilities of the standard reports, and recreate
                        your reports from scratch, if necessary.
                        However, if this would be too inconvenient, there is a possibility that opening a support ticket might help,
                        based on your specific case.
                        The custom financial reports that are being lost in this migration are the following ones:
                    </summary>
                    <ul>{}</ul>
                </details>
            """.format(" ".join([f"<li>{name} (id: {id})</li>" for id, name in custom_fin_reports])),
            category="Financial Reports",
            format="html",
        )
        return  # nosemgrep: no-early-return

    fin_report_ids = tuple(res[0] for res in custom_fin_reports)

    # create temporary column to have mapping between the old and the new report ids
    util.create_column(cr, "account_report", "v15_fin_report_id", "integer")

    # migrate custom financial reports from account_financial_html_report to account_report
    cr.execute(
        """
        INSERT INTO account_report (
            create_uid, write_uid, create_date, write_date, name,
            filter_unfold_all, filter_analytic, filter_period_comparison, filter_journals, filter_multi_company,
            filter_date_range, default_opening_date_filter,
            country_id, availability_condition,
            only_tax_exigible, v15_fin_report_id
        )
        SELECT create_uid, write_uid, create_date, NOW(), JSONB_BUILD_OBJECT('en_US', name),
               unfold_all_filter, analytic, comparison, show_journal_filter, 'selector',
               date_range, CASE WHEN date_range THEN 'this_year' ELSE 'today' END,
               country_id, CASE WHEN country_id IS NOT NULL THEN 'country' ELSE 'always' END,
               tax_report, id
          FROM account_financial_html_report
         WHERE id IN %s
     RETURNING id, name->>'en_US'
        """,
        [fin_report_ids],
    )

    new_custom_fin_reports = cr.fetchall()

    cr.execute(
        """
        INSERT INTO account_report_column (
            create_uid, write_uid, create_date, write_date,
            report_id, name, expression_label, figure_type,
            sortable, blank_if_zero
        )
        SELECT create_uid, write_uid, create_date, NOW(),
               id, JSONB_BUILD_OBJECT('en_US', 'Balance'), 'balance', 'monetary',
               True, False
          FROM account_report
         WHERE v15_fin_report_id IS NOT NULL
        """
    )

    # update ir_action_client context for migrated reports
    cr.execute(
        """
        UPDATE ir_act_client iac
           SET context = '{"report_id": ' || ar.id || '}'
          FROM account_report ar
          JOIN account_financial_html_report afhr
            ON afhr.id = ar.v15_fin_report_id
           AND ar.v15_fin_report_id IS NOT NULL
          JOIN ir_ui_menu ium
            ON ium.id = afhr.generated_menu_id
         WHERE iac.id = SPLIT_PART(ium.action, ',', 2)::integer
        """
    )

    # preserve menus and actions
    cr.execute(
        """
        WITH to_preserve AS (
            SELECT afhr.generated_menu_id,
                   SPLIT_PART(ium.action, ',', 2)::integer AS action_id
              FROM account_financial_html_report afhr
              JOIN ir_ui_menu ium
                ON ium.id = afhr.generated_menu_id
             WHERE afhr.id IN %s
        )
        UPDATE ir_model_data imd
           SET noupdate = True,
               name = REPLACE(imd.name, 'account_financial_html_report', 'account_report')
          FROM to_preserve
         WHERE (imd.res_id, imd.model) IN (
                   (to_preserve.generated_menu_id, 'ir.ui.menu'),
                   (to_preserve.action_id, 'ir.actions.client')
               )
        """,
        [fin_report_ids],
    )

    cr.execute(
        "UPDATE account_financial_html_report SET generated_menu_id = NULL WHERE id IN %s",
        [fin_report_ids],
    )

    # create temporary column to have mapping between the old and the new report line ids (for parent_id)
    util.create_column(cr, "account_report_line", "v15_fin_line_id", "integer")

    # create temporary columns for fields that are to be migrated to account_report_expression
    util.create_column(cr, "account_report_line", "v15_formulas", "varchar")
    util.create_column(cr, "account_report_line", "v15_figure_type", "varchar")
    util.create_column(cr, "account_report_line", "v15_green_on_positive", "bool")
    util.create_column(cr, "account_report_line", "v15_special_date_changer", "varchar")
    util.create_column(cr, "account_report_line", "v15_domain", "varchar")

    # constant regexes
    DOMAIN_EXPR_REGEX = r"-?sum(?:_if_(?:pos|neg)(?:_groupby)?)?"

    # migrate custom reports' lines from account_financial_html_report_line to account_report_line
    cr.execute(
        r"""
        WITH mapping AS (
            SELECT ar.id AS report_id,
                   afhrl.id AS line_id
              FROM account_report ar
              JOIN account_financial_html_report_line afhrl
                ON afhrl.financial_report_id = ar.v15_fin_report_id
               AND ar.v15_fin_report_id IS NOT NULL
        )
        INSERT INTO account_report_line (
            create_uid, write_uid, create_date, write_date,
            report_id, name,
            hierarchy_level, sequence, action_id, code, print_on_new_page, hide_if_zero,
            groupby,
            foldable, v15_domain,
            v15_green_on_positive, v15_special_date_changer, v15_fin_line_id,
            v15_formulas,
            v15_figure_type
        )
        SELECT afhrl.create_uid, afhrl.write_uid, afhrl.create_date, NOW(),
               m.report_id, JSONB_BUILD_OBJECT('en_US', afhrl.name),
               1, afhrl.sequence, afhrl.action_id, afhrl.code, afhrl.print_on_new_page, afhrl.hide_if_zero,
               CASE
                    WHEN afhrl.formulas ~ %s THEN afhrl.groupby
                    ELSE NULL
               END,
               afhrl.groupby IS NOT NULL AND afhrl.show_domain = 'foldable', afhrl.domain,
               afhrl.green_on_positive, afhrl.special_date_changer, afhrl.id,
               REGEXP_REPLACE(afhrl.formulas, '(\w+)', '\1.balance', 'g'),
               CASE
                    WHEN afhrl.figure_type = 'float' THEN NULL
                    WHEN afhrl.figure_type = 'percents' THEN 'percentage'
                    WHEN afhrl.figure_type = 'no_unit' THEN 'none'
                    ELSE 'monetary'
               END
          FROM mapping m
          JOIN account_financial_html_report_line afhrl
            ON afhrl.id = m.line_id
        """,
        [f"^{DOMAIN_EXPR_REGEX}$"],
    )

    # migrate custom reports' lines, that were children of other migrated lines (for which financial_report_id was not set in v15)
    while cr.rowcount:
        cr.execute(
            r"""
            WITH mapping AS (
                SELECT arl.report_id,
                       arl.id AS parent_id,
                       arl.hierarchy_level AS parent_hierarchy_level,
                       afhrl.id AS line_id
                  FROM account_financial_html_report_line afhrl
                  JOIN account_report_line arl
                    ON arl.v15_fin_line_id = afhrl.parent_id
                   AND NOT EXISTS (SELECT 1 FROM account_report_line WHERE v15_fin_line_id = afhrl.id)
            )
            INSERT INTO account_report_line (
                create_uid, write_uid, create_date, write_date,
                report_id, name,
                parent_id, hierarchy_level, sequence, action_id, code, print_on_new_page, hide_if_zero,
                groupby,
                foldable, v15_domain,
                v15_green_on_positive, v15_special_date_changer, v15_fin_line_id,
                v15_formulas,
                v15_figure_type
            )
            SELECT afhrl.create_uid, afhrl.write_uid, afhrl.create_date, NOW(),
                   m.report_id, JSONB_BUILD_OBJECT('en_US', afhrl.name),
                   m.parent_id, m.parent_hierarchy_level + 2, afhrl.sequence, afhrl.action_id, afhrl.code, afhrl.print_on_new_page, afhrl.hide_if_zero,
                   CASE
                        WHEN afhrl.formulas ~ %s THEN afhrl.groupby
                        ELSE NULL
                   END,
                   afhrl.groupby IS NOT NULL AND afhrl.show_domain = 'foldable', afhrl.domain,
                   afhrl.green_on_positive, afhrl.special_date_changer, afhrl.id,
                   REGEXP_REPLACE(afhrl.formulas, '(\w+)', '\1.balance', 'g'),
                   CASE
                        WHEN afhrl.figure_type = 'float' THEN NULL
                        WHEN afhrl.figure_type = 'percents' THEN 'percentage'
                        WHEN afhrl.figure_type = 'no_unit' THEN 'none'
                        ELSE 'monetary'
                   END
              FROM mapping m
              JOIN account_financial_html_report_line afhrl
                ON afhrl.id = m.line_id
            """,
            [f"^{DOMAIN_EXPR_REGEX}$"],
        )

    # v15_fin_report_id no longer needed
    util.remove_column(cr, "account_report", "v15_fin_report_id")

    # restore lines order (`sequence` field)
    # in v15 a line's `sequence` would only compare to its siblings to establish the order among themselves
    # in v16 lines are sorted purely by the (sequence, id). Meaning that if you have the following 3 lines:
    #   * A, sequence 1
    #   * A1, sequence 3, parent_id = A, hierarchy_level = 2
    #   * B, sequence 2
    # they will display as follows:
    #   * A
    #   * B
    #       * A1
    # which was never the case in v15 (parent-child relationship was alwasy respected no matter the value of `sequence`)
    # The following query translates v15 conventions into v16 rules through the use of `sort` a column made up of each ancestors'
    # sequence and their old `v15_fin_line_id` (used as a tiebreaker for siblings with same `sequence`).
    cr.execute(
        """
        WITH RECURSIVE _lines AS (
            SELECT id,
                   LPAD(sequence::text, 5, '0') || '.' || LPAD(v15_fin_line_id::text, 5, '0') AS sort,
                   report_id
              FROM account_report_line
             WHERE parent_id IS NULL
               AND v15_fin_line_id IS NOT NULL

             UNION ALL

            SELECT arl.id,
                   l.sort || '.' || LPAD(arl.sequence::text, 5, '0') || '.' || LPAD(arl.v15_fin_line_id::text, 5, '0') AS sort,
                   arl.report_id
              FROM account_report_line arl
              JOIN _lines l
                ON l.id = arl.parent_id
        ),
        _lines_ordered AS (
            SELECT id,
                   (ROW_NUMBER() OVER (PARTITION BY report_id ORDER BY sort))*10 AS sequence
              FROM _lines
        )
        UPDATE account_report_line arl
           SET sequence = lo.sequence
          FROM _lines_ordered lo
         WHERE arl.id = lo.id
        """
    )

    # populate account_report_expression with formulas and other fields from report lines
    cr.execute(
        """
        INSERT INTO account_report_expression (
            create_uid, write_uid, create_date, write_date,
            report_line_id, label,
            date_scope,
            figure_type, green_on_positive, auditable,
            engine,
            formula,
            subformula
        )
        SELECT arl.create_uid, arl.write_uid, arl.create_date, NOW(),
               arl.id, 'balance',
               COALESCE(arl.v15_special_date_changer, 'strict_range'),
               arl.v15_figure_type, arl.v15_green_on_positive, True,
               -- engine
               -- note that some formulas might contain both domain and aggregation terms. Those will be labelled as 'aggregation'
               -- and split in the end-10-migrate_financial_reports.py script.
                  CASE WHEN arl.v15_formulas ~ %(re)s THEN 'domain'
                       ELSE 'aggregation'
                  END,

               -- formula
                  CASE
                       WHEN arl.v15_formulas ~ %(re)s THEN COALESCE(arl.v15_domain, '[]')
                       ELSE COALESCE(arl.v15_formulas, 'sum_children')
                  END,

               -- subformula
                  CASE
                       WHEN arl.v15_formulas ~ %(re)s THEN REPLACE(arl.v15_formulas, '.balance', '')
                       ELSE NULL
                  END
          FROM account_report_line arl
         WHERE arl.v15_fin_line_id IS NOT NULL
        """,
        {"re": rf"^{DOMAIN_EXPR_REGEX}\.balance$"},
    )

    # account.report.line v15 temporary columns are no longer needed
    # note that `v15_fin_line_id` and `v15_domain` columns are deliberately not removed, to be used and removed in a later script
    util.remove_column(cr, "account_report_line", "v15_formulas")
    util.remove_column(cr, "account_report_line", "v15_figure_type")
    util.remove_column(cr, "account_report_line", "v15_green_on_positive")
    util.remove_column(cr, "account_report_line", "v15_special_date_changer")

    # some expressions may reference codes of lines from different reports, their `subformula` needs to be set to "cross_report"
    cr.execute(
        r"""
        WITH expression_code AS (
            SELECT REGEXP_SPLIT_TO_TABLE(
                       REGEXP_REPLACE(are.formula, '(?:^-|\.balance|\(|\))', '', 'g'),
                       '[\s\+\*\-/]+'
                    ) AS code,
                    are.id AS expression_id,
                    arl.report_id AS report_id
              FROM account_report_expression are
              JOIN account_report_line arl
                ON arl.id = are.report_line_id
             WHERE are.engine = 'aggregation'
               AND are.subformula IS NULL
               AND are.formula != 'sum_children'
        ),
        cross_report_expression AS (
            SELECT c.expression_id
              FROM expression_code c
                -- the LEFT JOIN here is used to make sure that no line with such code is present in the same report.
                -- This assumes that, in such case, another line with such code must exist in a different report.
                -- (otherwise the report would be broken before the upgrade)
         LEFT JOIN account_report_line arl
                ON arl.code = c.code
               AND arl.report_id = c.report_id
             WHERE arl IS NULL
             GROUP BY c.expression_id
        )
        UPDATE account_report_expression are
           SET subformula = 'cross_report'
          FROM cross_report_expression e
         WHERE are.id = e.expression_id
        """
    )

    # temp table, used and dropped in end- script
    cr.execute(
        """
        CREATE UNLOGGED TABLE ___upgrade_afhrl AS
            SELECT *
              FROM account_financial_html_report_line afhrl
             WHERE NOT EXISTS (SELECT 1 FROM account_report_line WHERE code = afhrl.code)
        """
    )

    util.add_to_migration_reports(
        """
            <details>
                <summary>
                    The following custom financial reports have been migrated, note however they might be partially or substantially
                    wrong.
                    It is therefore crucial to analyze them thouroughlly and either fix the errors or create them anew.
                </summary>
                <ul>{}</ul>
            </details>
        """.format(
            " ".join(
                [
                    f"<li>{util.get_anchor_link_to_record('account.report', id, name)}</li>"
                    for id, name in new_custom_fin_reports
                ]
            )
        ),
        category="Accounting reports",
        format="html",
    )
