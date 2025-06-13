from odoo.upgrade import util


def migrate(cr, version):
    tags_to_migrate = (
        "tag_diot_16",  # tax_report_mx_diot_paid_16_tag
        "tag_diot_16_non_cre",  # tax_report_mx_diot_paid_16_non_cred_tag
        "tag_diot_8",  # tax_report_mx_diot_paid_8_tag
        "tag_diot_8_non_cre",  # tax_report_mx_diot_paid_8_non_cred_tag
        "tag_diot_16_imp",  # tax_report_mx_diot_importation_16_tag
        "tag_diot_0",  # tax_report_mx_diot_paid_0_tag
        "tag_diot_exento",  # tax_report_mx_diot_exempt_tag
        "tag_diot_ret",  # tax_report_mx_diot_withheld_tag
        # DIOT 2025 rework new tags
        "tag_diot_8_south",
        "tag_diot_8_south_non_cre",
        "tag_diot_16_imp_non_cre",
        "tag_diot_16_imp_int",
        "tag_diot_16_imp_int_non_cre",
        "tag_diot_8_refund",
        "tag_diot_8_south_refund",
        "tag_diot_16_refund",
        "tag_diot_16_imp_refund",
        "tag_diot_16_imp_int_refund",
        "tag_diot_exento_imp",
        "tag_diot_no_obj",
    )

    # Fetch (tax) tags to migrate.
    cr.execute(
        """
        SELECT res_id
          FROM ir_model_data
         WHERE module = 'l10n_mx'
           AND name IN %s
        """,
        [tags_to_migrate],
    )

    old_tag_ids = [row[0] for row in cr.fetchall()]

    # Create temporary table with tags <-> aml relation for tags that will get migrated.
    cr.execute(
        """
        CREATE TABLE l10n_mx_aml_with_tags_to_replace (
            line_id,
            xmlid,
            debit
        ) AS (
            SELECT aml.id,
                   imd.name,
                   aml.debit
              FROM account_move_line AS aml
              JOIN account_account_tag_account_move_line_rel AS tag_rel
                ON tag_rel.account_move_line_id = aml.id
              JOIN ir_model_data AS imd
                ON imd.model = 'account.account.tag'
               AND imd.res_id = tag_rel.account_account_tag_id
             WHERE tag_rel.account_account_tag_id IN %s
        )
        """,
        [tuple(old_tag_ids)],
    )

    # Delete all relations with tags to migrate.
    cr.execute(
        """
        DELETE FROM account_account_tag_account_move_line_rel
              WHERE account_account_tag_id IN %s
        """,
        [tuple(old_tag_ids)],
    )

    # Create temporary table with all the taxes that use the tags to be migrated
    cr.execute(
        """
        CREATE TABLE l10n_mx_tax_id_with_tag_diot_ret (
          id
        ) AS (
          SELECT DISTINCT tax.id
            FROM account_tax AS tax
            JOIN account_tax_repartition_line AS rep_line
              ON rep_line.tax_id = tax.id
            JOIN account_account_tag_account_tax_repartition_line_rel AS rep_line_rel
              ON rep_line_rel.account_tax_repartition_line_id = rep_line.id
            JOIN ir_model_data imd
              ON imd.module = 'l10n_mx'
             AND imd.name = 'tag_diot_ret'
             AND imd.res_id = rep_line_rel.account_account_tag_id
        )
      """
    )

    # Delete records for tags and  account_tax_repartion_lines to migrate.
    cr.execute(
        """
        DELETE FROM account_account_tag_account_tax_repartition_line_rel
              WHERE account_account_tag_id IN %s
        """,
        [tuple(old_tag_ids)],
    )

    # Remove old tags.
    for tag in tags_to_migrate:
        util.remove_record(cr, f"l10n_mx.{tag}")
