# -*- coding: utf-8 -*-
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
    }.get(xml_id, xml_id.split(".")[0][5:])


def migrate(cr, version):
    util.remove_field(cr, "account.tax", "real_amount")

    # Remove templates m2o and replace by new code
    for model in ("res.company", "account.report"):
        table = util.table_of_model(cr, model)
        util.create_column(cr, table, "chart_template", "varchar")
        cr.execute(
            f"""
        SELECT record.id,
               data.module || '.' || data.name AS template_xml_id
          FROM {table} record
          JOIN ir_model_data data ON data.res_id = record.chart_template_id
                                 AND data.model = 'account.chart.template'
        """
        )
        for record_id, template_xml_id in cr.fetchall():
            cr.execute(
                f"UPDATE {table} SET chart_template = %s WHERE id = %s", [chart_mapper(template_xml_id), record_id]
            )
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
        cr.execute(
            f"""
            INSERT INTO ir_property (name, company_id, fields_id, value_reference, type)
                  SELECT f.name, c.id, f.id, concat('account.account,', c.{fname}), 'many2one'
                    FROM res_company c
                    JOIN ir_model_fields f
                      ON f.model = 'product.category'
                     AND f.name = %s
                   WHERE c.{fname} IS NOT NULL
            ON CONFLICT DO NOTHING
        """,
            [fname],
        )
        util.remove_field(cr, "res.company", fname)

    # Make property fields on account.tax.group real fields
    # tax.group object is not shared anymore within companies, so we need to duplicate them and populate
    # the new fields with the previous ir.property values
    columns = util.get_columns(cr, "account_tax_group", ignore=["id"])
    util.create_column(cr, "account_tax_group", "company_id", "int")
    util.create_column(cr, "account_tax_group", "_tmp_orig_id", "int")
    cr.execute(
        f"""
        INSERT INTO account_tax_group ({', '.join(columns)}, company_id, _tmp_orig_id)
             SELECT {', '.join('tg.%s' % f for f in columns)}, company.id, tg.id
               FROM account_tax_group tg,
                    res_company company
              WHERE company.chart_template IS NOT NULL
    """
    )
    company_fk = {table: column for table, column, _, _ in util.get_fk(cr, "res_company")}
    for table, column, _, _ in util.get_fk(cr, "account_tax_group"):
        if table in company_fk:
            cr.execute(
                f"""
                UPDATE {table} relation
                   SET {column} = new.id
                  FROM account_tax_group new
                 WHERE relation.{column} = new._tmp_orig_id
                   AND relation.{company_fk[table]} = new.company_id
            """
            )
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
    util.remove_column(cr, "account_tax_group", "_tmp_orig_id")
    for fname in [
        "tax_payable_account_id",
        "tax_receivable_account_id",
        "advance_tax_payment_account_id",
    ]:
        old_fname = "property_%s" % fname
        util.rename_field(cr, "account.tax.group", old_fname, fname)
        util.create_column(cr, "account_tax_group", fname, "int")
        cr.execute(
            f"""
              WITH to_update AS (
                SELECT tg.id,
                       SPLIT_PART(COALESCE(prop.value_reference, default_prop.value_reference), ',', 2)::int AS account_id
                  FROM account_tax_group tg
                  JOIN ir_model_fields field ON field.name = %(fname)s
                                            AND field.model = 'account.tax.group'
             LEFT JOIN ir_property default_prop ON default_prop.fields_id = field.id
                                               AND default_prop.company_id = tg.company_id
             LEFT JOIN ir_property prop ON prop.fields_id = field.id
                                       AND prop.company_id = tg.company_id
                                       AND prop.res_id = 'account.tax.group,' || tg.id
                   )
            UPDATE account_tax_group
               SET {fname} = to_update.account_id
              FROM to_update
             WHERE account_tax_group.id = to_update.id
        """,
            {"fname": fname},
        )
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

    util.move_field_to_module(cr, "account.move", "amount_total_words", "l10n_dz", "account")
    util.move_field_to_module(cr, "account.move", "amount_total_words", "l10n_in", "account")

    util.create_column(cr, "account_payment_term_line", "delay_type", "varchar")
    util.rename_field(cr, "account.payment.term.line", "days", "nb_days")
    cr.execute(
        """
        UPDATE account_payment_term_line
           SET delay_type = CASE
                   WHEN months = 0 THEN 'days_after'
                   WHEN months = 1 THEN 'days_after_end_of_month'
                   ELSE 'days_after_end_of_next_month'
               END
         WHERE months >= 0
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
