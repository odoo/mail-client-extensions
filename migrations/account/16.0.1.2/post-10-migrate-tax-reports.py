from odoo.upgrade import util


def migrate(cr, version):
    tax_report_ids = util.ENVIRON.get("upgrade_custom_tax_report_ids_16")

    if not tax_report_ids:
        return

    # create temporary column to have mapping between the old and the new report ids
    util.create_column(cr, "account_report", "v15_tax_report_id", "integer")

    # migrate custom tax reports from account_tax_report to account_report
    cr.execute(
        """
        INSERT INTO account_report (
            create_uid, write_uid, create_date, write_date,
            name, v15_tax_report_id, root_report_id,
            country_id, availability_condition
        )
        SELECT create_uid, write_uid, create_date, NOW(),
               JSONB_BUILD_OBJECT('en_US', name), id, %s,
               country_id, CASE WHEN country_id IS NOT NULL THEN 'country' ELSE 'always' END
          FROM account_tax_report
         WHERE id IN %s
     RETURNING id, name->>'en_US'
        """,
        [util.ref(cr, "account.generic_tax_report"), tax_report_ids],
    )

    new_custom_tax_reports = cr.fetchall()

    # recompute fields dependent on `root_report_id`
    util.recompute_fields(
        cr,
        "account.report",
        [
            "only_tax_exigible",
            "availability_condition",
            "default_opening_date_filter",
            "filter_multi_company",
            "filter_date_range",
            "filter_show_draft",
            "filter_unreconciled",
            "filter_unfold_all",
            "filter_period_comparison",
            "filter_growth_comparison",
            "filter_journals",
            "filter_analytic",
            "filter_hierarchy",
            "filter_account_type",
            "filter_partner",
            "filter_fiscal_position",
        ],
        ids=[id for id, _ in new_custom_tax_reports],
    )

    cr.execute(
        """
        INSERT INTO account_report_column (
            create_uid, write_uid, create_date, write_date,
            report_id, name,
            expression_label, figure_type, blank_if_zero
        )
        SELECT create_uid, write_uid, create_date, NOW(),
               id, JSONB_BUILD_OBJECT('en_US', 'Balance'),
               'balance', 'monetary', False
          FROM account_report
         WHERE v15_tax_report_id IS NOT NULL
        """
    )

    # Odoo 16's `account_report_line` has a unique constraint on `code` that was not present in `account_tax_report_line` in v15
    # OTOH, in v15, there was no concept of `cross_report` references (formulas that would refer lines in separate reports),
    # Therefore, for most cases it will be enough to rename non-unique codes by appending their report_id and appropriately
    # replacing their occurrences in the report's formulas.
    cr.execute(
        r"""
        WITH not_uniq_codes AS (
            SELECT code
              FROM account_tax_report_line
             WHERE code IS NOT NULL
             GROUP BY code
            HAVING COUNT(*) > 1
        ),
        renamed_codes AS (
            UPDATE account_tax_report_line atrl
               SET code = atrl.code || '_R' || ar.id
              FROM not_uniq_codes c,
                   account_report ar
             WHERE c.code = atrl.code
               AND ar.v15_tax_report_id = atrl.report_id
         RETURNING c.code AS old_code, atrl.code AS new_code, atrl.report_id
        )
        UPDATE account_tax_report_line atrl
           SET formula = REGEXP_REPLACE(formula, '\m' || rc.old_code || '\M', rc.new_code, 'g')
          FROM renamed_codes rc
         WHERE atrl.report_id = rc.report_id
        """
    )

    # `code` values were always meant to be words composed of:
    #   * Letters:          [a-zA-Z]
    #   * Digits:           [0-9]
    #   * Underscores:      `_`
    # with one caveat: not to be a "pure number", i.e. to include at least one letter/underscore.
    # However, differently from Odoo 16, this rule was not enforced in v15, making it possible to treat a number (e.g. 16) as a valid code.
    # Editing such codes, by appending a string to it:
    cr.execute(
        r"""
        WITH renamed_codes AS (
            UPDATE account_tax_report_line atrl
               SET code = code || '_upg_fix'
             WHERE code ~ '^\d+$'
         RETURNING LEFT(code, -LENGTH('_upg_fix')) AS old_code
        ),
        grouped_codes AS (
            SELECT atrl.id, ARRAY_TO_STRING(ARRAY_AGG(rc.old_code), '|') AS old_code
              FROM renamed_codes rc
              JOIN account_tax_report_line atrl
                ON atrl.formula IS NOT NULL
               AND atrl.formula ~ ('\m' || rc.old_code || '\M')
             GROUP BY atrl.id
        )
        UPDATE account_tax_report_line atrl
           SET formula = REGEXP_REPLACE(formula, '\m(' || gc.old_code || ')\M', '\1_upg_fix', 'g')
          FROM grouped_codes gc
         WHERE atrl.id = gc.id
        """
    )

    # create temporary column to have mapping between the old and the new report line ids (for parent_id)
    util.create_column(cr, "account_report_line", "v15_tax_line_id", "integer")

    # create temporary columns for columns to be migrated to account_report_expression
    util.create_column(cr, "account_report_line", "v15_formula", "varchar")
    util.create_column(cr, "account_report_line", "v15_tag_name", "varchar")

    # migrate custom reports' lines from account_tax_report_line to account_report_line
    cr.execute(
        r"""
        INSERT INTO account_report_line (
            create_uid, write_uid, create_date, write_date,
            report_id, name,
            hierarchy_level, sequence,
            action_id, code, v15_tax_line_id,
            v15_formula, v15_tag_name
        )
        SELECT atrl.create_uid, atrl.write_uid, atrl.create_date, NOW(),
               ar.id, JSONB_BUILD_OBJECT('en_US', atrl.name),
               ARRAY_LENGTH(STRING_TO_ARRAY(RTRIM(atrl.parent_path, '/'), '/'), 1), atrl.sequence,
               atrl.report_action_id, atrl.code, atrl.id,
               atrl.formula, atrl.tag_name
          FROM account_tax_report_line atrl
          JOIN account_report ar
            ON ar.v15_tax_report_id = atrl.report_id
        """
    )

    # remove temp column v15_tax_report_id
    util.remove_column(cr, "account_report", "v15_tax_report_id")

    # remap v15 parent_id to new line ids
    cr.execute(
        """
        UPDATE account_report_line arl
           SET parent_id = arl2.id
          FROM account_report_line arl2
          JOIN account_tax_report_line atrl
            ON atrl.parent_id = arl2.v15_tax_line_id
         WHERE arl.v15_tax_line_id = atrl.id
        """
    )

    # restore lines order (`sequence` column)
    # in v15 a line's `sequence` would only compare to its siblings to establish the order among themselves
    # in v16 lines are sorted purely by the (sequence, id). Meaning that if you have the following 3 lines:
    #   * A, sequence 1
    #   * A1, sequence 3, parent_id = A, hierarchy_level = 2
    #   * B, sequence 2
    # they will display as follows:
    #   * A
    #   * B
    #       * A1
    # which was never the case in v15 (parent-child relationship was always respected no matter the value of `sequence`)
    # The following query translates v15 conventions into v16 rules through the use of `sort`, a column made up of each ancestors'
    # sequence and their old  v15_tax_line_id` (used as a tiebreaker for siblings with same `sequence`).
    cr.execute(
        """
        WITH RECURSIVE _lines AS (
            SELECT id,
                   LPAD(sequence::text, 5, '0') || '.' || LPAD(v15_tax_line_id::text, 5, '0') AS sort,
                   report_id
              FROM account_report_line
             WHERE parent_id IS NULL
               AND v15_tax_line_id IS NOT NULL

             UNION ALL

            SELECT arl.id,
                   l.sort || '.' || LPAD(arl.sequence::text, 5, '0') || '.' || LPAD(arl.v15_tax_line_id::text, 5, '0') AS sort,
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

    # temporary column storing old report line id no longer needed
    util.remove_column(cr, "account_report_line", "v15_tax_line_id")

    # should match words made up of letters, digits and _, with at least one letter/underscore (no pure number).
    TERM_CODE_REGEX = r"\m\w+\M(?<!\m\d+)"

    # populate account_report_expression with report lines formula and tag_name fields
    cr.execute(
        rf"""
        INSERT INTO account_report_expression (
            create_uid, write_uid, create_date, write_date,
            report_line_id, label, auditable, date_scope,
            engine,
            formula
        )
        SELECT arl.create_uid, arl.write_uid, arl.create_date, NOW(),
               arl.id, 'balance', True, 'strict_range',
               -- engine
                  CASE WHEN arl.v15_tag_name IS NOT NULL THEN 'tax_tags'
                       ELSE 'aggregation'
                  END,

               -- formula
                  CASE
                       WHEN arl.v15_tag_name IS NOT NULL THEN arl.v15_tag_name
                       WHEN arl.v15_formula IS NOT NULL THEN REGEXP_REPLACE(arl.v15_formula, '({TERM_CODE_REGEX})', '\1.balance', 'g')
                       ELSE 'sum_children'
                  END
          FROM account_report_line arl
        """
    )

    # account.report.line temporary columns are no longer needed
    util.remove_column(cr, "account_report_line", "v15_formula")
    util.remove_column(cr, "account_report_line", "v15_tag_name")

    util.add_to_migration_reports(
        """
            <details>
                <summary>
                    The following custom tax reports have been migrated, note however they might be partially or substantially wrong.
                    It is therefore crucial to analyze them thoroughly and either fix the errors or create them anew.
                </summary>
                <ul>%s</ul>
            </details>
        """
        % " ".join(
            [
                f"<li>{util.get_anchor_link_to_record('account.report', id, name)}</li>"
                for id, name in new_custom_tax_reports
            ]
        ),
        category="Tax reports",
        format="html",
    )
