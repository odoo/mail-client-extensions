from odoo.tools.sql import index_exists

from odoo.upgrade import util


def chart_mapper(xml_id):
    return {
        "account.configurable_chart_template": "generic_coa",
        "l10n_ar.l10nar_base_chart_template": "ar_base",
        "l10n_ar.l10nar_ex_chart_template": "ar_ex",
        "l10n_ar.l10nar_ri_chart_template": "ar_ri",
        "l10n_es.account_chart_template_assoc": "es_assec",
        "l10n_es.account_chart_template_common": "es_common",
        "l10n_es.account_chart_template_full": "es_full",
        "l10n_es.account_chart_template_pymes": "es_pymes",
        "l10n_se.l10nse_chart_template_K2": "se_K2",
        "l10n_se.l10nse_chart_template_K3": "se_K3",
        "l10n_ua.l10n_ua_ias_chart_template": "ua_ias",
        "l10n_ua.l10n_ua_psbo_chart_template": "ua_psbo",
        "l10n_de.l10n_de_chart_template": "de_skr03",
        "l10n_de.l10n_chart_de_skr04": "de_skr04",
    }.get(xml_id, xml_id.split(".")[0][5:])


def migrate(cr, version):
    util.remove_field(cr, "account.tax", "real_amount")

    # Remove templates m2o and replace by new code
    for model in ("res.company", "account.report"):
        table = util.table_of_model(cr, model)
        util.create_column(cr, table, "chart_template", "varchar")
        query = util.format_query(
            cr,
            """
        SELECT record.id,
               data.module || '.' || data.name AS template_xml_id
          FROM {table} record
          JOIN ir_model_data data ON data.res_id = record.chart_template_id
                                 AND data.model = 'account.chart.template'
            """,
            table=table,
        )
        cr.execute(query)
        for record_id, template_xml_id in cr.fetchall():
            query = util.format_query(cr, "UPDATE {} SET chart_template = %s WHERE id = %s", table)
            cr.execute(query, [chart_mapper(template_xml_id), record_id])

        util.remove_field(cr, model, "chart_template_id")
    util.remove_field(cr, "res.config.settings", "chart_template_id")

    # Delete the templates
    for model in [
        "account.fiscal.position.tax",
        "account.fiscal.position.account",
        "account.fiscal.position",
        "account.reconcile.model",
        "account.reconcile.model.line",
        "account.tax.repartition.line",
        "account.tax",
        "account.account",
        "account.group",
        "account.chart",
    ]:
        util.remove_model(cr, f"{model}.template")

    # Replace double m2o by single m2o + type field
    util.create_column(cr, "account_tax_repartition_line", "tax_id", "int")
    util.create_column(cr, "account_tax_repartition_line", "document_type", "varchar")
    query = """
        UPDATE account_tax_repartition_line
           SET tax_id = COALESCE(invoice_tax_id, refund_tax_id),
               document_type = CASE
                   WHEN invoice_tax_id IS NOT NULL THEN 'invoice'
                   ELSE 'refund'
               END
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_tax_repartition_line"))
    util.remove_field(cr, "account.tax.repartition.line", "invoice_tax_id")
    util.remove_field(cr, "account.tax.repartition.line", "refund_tax_id")

    # Replace fake property fields on company by true property fields
    for fname in [
        "property_stock_account_input_categ_id",
        "property_stock_account_output_categ_id",
        "property_stock_valuation_account_id",
    ]:
        query = util.format_query(
            cr,
            """
            INSERT INTO ir_property (name, company_id, fields_id, value_reference, type)
                  SELECT f.name, c.id, f.id, concat('account.account,', c.{fname}), 'many2one'
                    FROM res_company c
                    JOIN ir_model_fields f
                      ON f.model = 'product.category'
                     AND f.name = %s
                   WHERE c.{fname} IS NOT NULL
            ON CONFLICT DO NOTHING
            """,
            fname=fname,
        )
        cr.execute(query, [fname])
        util.remove_field(cr, "res.company", fname)

    # Make property fields on account.tax.group real fields
    # tax.group object is not shared anymore within companies, so we need to duplicate them and populate
    # the new fields with the previous ir.property values
    columns = util.get_columns(cr, "account_tax_group", ignore=["id"])
    util.create_column(cr, "account_tax_group", "company_id", "int")
    util.create_column(cr, "account_tax_group", "_tmp_orig_id", "int")

    # determine for which companies we should duplicate the tax groups
    company_fk = {table: column for table, column, _, _ in util.get_fk(cr, "res_company", quote_ident=False)}
    tax_group_fks = [
        (table, column)
        for table, column, _, _ in util.get_fk(cr, "account_tax_group", quote_ident=False)
        if table in company_fk
    ]

    cte = " UNION ".join(
        util.format_query(
            cr,
            """
            SELECT {fk} AS id,
                   {column} AS tg_id
              FROM {table}
             WHERE {fk} IS NOT NULL
               AND {column} IS NOT NULL
            """,
            fk=company_fk[table],
            table=table,
            column=column,
        )
        for table, column in tax_group_fks
    )

    query = util.format_query(
        cr,
        """
        WITH company AS (
            {cte}
        )
        INSERT INTO account_tax_group ({columns}, company_id, _tmp_orig_id)
             SELECT {tg_columns}, company.id, tg.id
               FROM account_tax_group tg,
                    company
              WHERE company.tg_id = tg.id
        """,
        cte=util.SQLStr(cte),
        columns=columns,
        tg_columns=columns.using(alias="tg"),
    )
    cr.execute(query)

    for table, column in tax_group_fks:
        query = util.format_query(
            cr,
            """
            UPDATE {table} relation
               SET {column} = new.id
              FROM account_tax_group new
             WHERE relation.{column} = new._tmp_orig_id
               AND relation.{fk} = new.company_id
            """,
            table=table,
            column=column,
            fk=company_fk[table],
        )
        if util.column_exists(cr, table, "id"):
            util.explode_execute(cr, query, table=table, alias="relation")
        else:
            cr.execute(query)

    cr.execute("""DELETE FROM account_tax_group WHERE company_id IS NULL""")
    cr.execute(
        """
        INSERT INTO ir_model_data (res_id, name, module, model, noupdate)
             SELECT DISTINCT ON (tg.company_id || '_' || origin_data.name)
                    tg.id,
                    tg.company_id || '_' || origin_data.name,
                    'account',
                    origin_data.model,
                    TRUE
               FROM account_tax_group tg
               JOIN ir_model_data origin_data ON origin_data.res_id = tg._tmp_orig_id
                                             AND origin_data.model = 'account.tax.group'
                                             AND origin_data.module LIKE 'l10n%'
        ON CONFLICT DO NOTHING
    """
    )
    cr.execute(
        """
        DELETE FROM ir_model_data data
              WHERE model = 'account.tax.group'
                AND module LIKE 'l10n%'
    """
    )
    for fname in [
        "tax_payable_account_id",
        "tax_receivable_account_id",
        "advance_tax_payment_account_id",
    ]:
        old_fname = f"property_{fname}"
        util.rename_field(cr, "account.tax.group", old_fname, fname)
        util.create_column(cr, "account_tax_group", fname, "int")
        query = util.format_query(
            cr,
            """
              WITH to_update AS (
                SELECT tg.id,
                       SPLIT_PART(COALESCE(prop.value_reference, default_prop.value_reference), ',', 2)::int AS account_id
                  FROM account_tax_group tg
                  JOIN ir_model_fields field ON field.name = %s
                                            AND field.model = 'account.tax.group'
             LEFT JOIN ir_property default_prop ON default_prop.fields_id = field.id
                                               AND default_prop.company_id = tg.company_id
                                               AND default_prop.res_id IS NULL
             LEFT JOIN ir_property prop ON prop.fields_id = field.id
                                       AND prop.company_id = tg.company_id
                                       AND prop.res_id = 'account.tax.group,' || tg._tmp_orig_id
                   )
            UPDATE account_tax_group
               SET {} = to_update.account_id
              FROM to_update
             WHERE account_tax_group.id = to_update.id
            """,
            fname,
        )
        cr.execute(query, [fname])

        cr.execute(
            """
            DELETE FROM ir_property p
                  USING ir_model_fields f
                  WHERE f.id = p.fields_id
                    AND f.model = 'account.tax.group'
                    AND f.name = %s
        """,
            [fname],
        )
    util.remove_column(cr, "account_tax_group", "_tmp_orig_id")
    util.move_field_to_module(cr, "account.move", "amount_total_words", "l10n_dz", "account")
    util.move_field_to_module(cr, "account.move", "amount_total_words", "l10n_in", "account")

    util.create_column(cr, "account_payment_term_line", "delay_type", "varchar")
    util.rename_field(cr, "account.payment.term.line", "days", "nb_days")
    cr.execute(
        """
        WITH all_totals AS (
            SELECT id,
                (months * 30) + nb_days AS total_days,
                CASE
                    WHEN (months * 30) + nb_days >= 30 AND end_month THEN 'days_after_end_of_next_month'
                    WHEN (months * 30) + nb_days < 30 AND end_month THEN 'days_after_end_of_month'
                    ELSE 'days_after'
                END AS delay_type
            FROM account_payment_term_line
        )
        UPDATE account_payment_term_line
        SET
            nb_days = CASE
                WHEN all_totals.delay_type = 'days_after' THEN all_totals.total_days
                WHEN days_after IS NOT NULL AND days_after > 0 THEN days_after
                ELSE nb_days
            END,
            delay_type = all_totals.delay_type
        FROM all_totals
        WHERE account_payment_term_line.id = all_totals.id;
        """
    )

    cr.execute(
        """
        WITH pt AS (
           SELECT t.id, SUM(l.value_amount) AS percentage
             FROM account_payment_term t
        LEFT JOIN account_payment_term_line l
               ON l.payment_id = t.id AND l.value = 'percent'
         GROUP BY t.id
        )
        UPDATE account_payment_term_line ptl
           SET value_amount = 100 - COALESCE(pt.percentage, 0.0)
          FROM pt
         WHERE pt.id = ptl.payment_id
           AND ptl.value = 'balance'
        """
    )
    cr.execute(
        """
        DELETE FROM account_payment_term_line
        WHERE value_amount = 0
        AND value = 'balance'
        """
    )
    cr.execute("UPDATE account_payment_term_line SET value = 'percent' WHERE value = 'balance'")
    util.remove_field(cr, "account.payment.term.line", "months")
    util.remove_field(cr, "account.payment.term.line", "day_of_the_month")
    util.delete_unused(cr, "account.account_payment_term_2months")

    util.create_column(cr, "account_payment_term", "early_pay_discount_computation", "varchar")
    util.create_column(cr, "account_payment_term", "discount_percentage", "numeric")
    util.create_column(cr, "account_payment_term", "discount_days", "int4")
    util.create_column(cr, "account_payment_term", "early_discount", "boolean")

    cr.execute(
        """
        WITH pay_term_line AS (
           SELECT payment_id
           FROM   account_payment_term_line
         WHERE discount_percentage > 0
         GROUP BY payment_id
        )
        UPDATE account_payment_term t
            SET early_discount = true
           FROM pay_term_line l
          WHERE l.payment_id = t.id
        """
    )
    cr.execute(
        """
        UPDATE account_payment_term t
           SET early_pay_discount_computation = c.early_pay_discount_computation
           FROM res_company c
         WHERE c.id = t.company_id
        """
    )
    cr.execute(
        """
        WITH ptl AS (
           SELECT payment_id,
                  MAX(discount_percentage) as discount_percentage,
                  MAX(discount_days) as discount_days
             FROM account_payment_term_line
         GROUP BY payment_id
        )
        UPDATE account_payment_term t
           SET discount_percentage = ptl.discount_percentage,
               discount_days = ptl.discount_days
           FROM ptl
         WHERE ptl.payment_id = t.id
        """
    )

    util.remove_field(cr, "res.company", "early_pay_discount_computation")
    util.remove_field(cr, "res.config.settings", "early_pay_discount_computation")
    util.remove_field(cr, "account.payment.term.line", "discount_percentage")
    util.remove_field(cr, "account.payment.term.line", "days_after")
    util.remove_field(cr, "account.payment.term.line", "end_month")
    util.remove_field(cr, "account.move.line", "discount_percentage")
    util.remove_field(cr, "account.payment.term.line", "discount_days")

    util.remove_field(cr, "res.config.settings", "group_show_line_subtotals_tax_excluded")
    util.remove_field(cr, "res.config.settings", "group_show_line_subtotals_tax_included")
    util.remove_record(cr, "account.group_show_line_subtotals_tax_excluded")
    util.remove_record(cr, "account.group_show_line_subtotals_tax_included")

    if util.module_installed(cr, "website_sale"):
        util.move_field_to_module(
            cr, "res.config.settings", "show_line_subtotals_tax_selection", "account", "website_sale"
        )
        util.remove_column(cr, "res_config_settings", "show_line_subtotals_tax_selection")
    else:
        util.remove_field(cr, "res.config.settings", "show_line_subtotals_tax_selection")

    # Wizard account.invoice.send replaced by account.move.send
    util.remove_model(cr, "account.invoice.send")

    util.create_column(cr, "res_partner_bank", "has_iban_warning", "boolean")
    util.create_column(cr, "res_partner_bank", "has_money_transfer_warning", "boolean")

    util.rename_field(cr, "account.tax", "description", "invoice_label")

    # De-duplicate the name so that the constraint UNIQUE UNDEX account_move_unique_name can
    # be added by the ORM
    query = """
        WITH to_update AS (
            SELECT move.id,
                   move.name,
                   row_number() OVER(ordered_move) AS row_seq
              FROM account_move move
              JOIN account_journal journal
                ON move.journal_id = journal.id
             WHERE move.state = 'posted'
               AND move.name != '/'
               AND journal.id = %s
            WINDOW ordered_move AS (PARTITION BY move.name, move.journal_id
                                        ORDER BY move.name, move.journal_id, move.date)
        )
        UPDATE account_move
           SET name = to_update.name || ' (' || (row_seq-1)::text || ')'
          FROM to_update
         WHERE account_move.id = to_update.id
           AND row_seq > 1
    """
    if not index_exists(cr, "account_move_unique_name_latam"):
        cr.execute("SELECT id FROM account_journal")
        util.parallel_execute(cr, [cr.mogrify(query, [jid]).decode() for (jid,) in cr.fetchall()])

    # Send & Print refactor: new field to link to the PDF sent
    util.explode_execute(
        cr,
        """
        UPDATE ir_attachment a
           SET res_field = 'invoice_pdf_report_file'
          FROM account_move m
         WHERE a.id = m.message_main_attachment_id
           AND res_field IS NULL
           AND mimetype = 'application/pdf'
        """,
        table="ir_attachment",
        alias="a",
    )
