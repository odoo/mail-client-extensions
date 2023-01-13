# -*- coding: utf-8 -*-
from odoo.addons.account.models.chart_template import update_taxes_from_templates

from odoo.upgrade import util


def migrate(cr, version):
    # Remove DIOT menuitems as it now is a variant of the tax report.
    util.remove_record(cr, "l10n_mx_reports.action_account_report_diot")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "l10n_mx_reports.account_reports_legal_mexican_statements_menu"),
            util.ref(cr, "l10n_mx_reports.menu_action_account_report_diot"),
        ],
    )

    # Make sure all taxes/tags are updated.
    update_taxes_from_templates(cr, "l10n_mx.mx_coa")

    tags_to_migrate = [
        ("tag_diot_16", "+DIOT: 16%"),
        ("tag_diot_8", "+DIOT: 8%"),
        ("tag_diot_0", "+DIOT: 0%"),
        ("tag_diot_16_non_cre", "+DIOT: 16% NO ACREDITABLE"),
        ("tag_diot_8_non_cre", "+DIOT: 8% NO ACREDITABLE"),
        ("tag_diot_16_imp", "+DIOT: 16% IMP"),
        ("tag_diot_exento", "+DIOT: Exento"),
        (None, "+DIOT: Refunds"),
        (None, "+DIOT: Retención"),
        (None, "-DIOT: Retención"),
    ]

    # Migrate tag_diot_16_non_cre, tag_diot_8_non_cre, tag_diot_16_imp,
    # tag_diot_exento, tag_diot_16, tag_diot_8, tag_diot_0:
    # The lines with debit get the mapped tag, the lines with credit get
    # the tax_report_mx_diot_refunds_tag.

    # Fetch the tags created by the report expressions.
    cr.execute(
        """
        SELECT id, name->>'en_US'
          FROM account_account_tag
         WHERE name->>'en_US' in %s
        """,
        [tuple([tag_name for _, tag_name in tags_to_migrate])],
    )

    map_tags_name_to_id = {name: id for id, name in cr.fetchall()}

    for old_tag_xmlid, tag_name in tags_to_migrate:
        if old_tag_xmlid:
            cr.execute(
                """
                INSERT INTO account_account_tag_account_move_line_rel(
                            account_move_line_id,
                            account_account_tag_id
                    )
                    SELECT repl.line_id,
                        CASE WHEN repl.debit > 0 THEN %s ELSE %s END
                    FROM l10n_mx_aml_with_tags_to_replace AS repl
                    WHERE repl.xmlid = %s
                """,
                [
                    map_tags_name_to_id[tag_name],
                    map_tags_name_to_id["+DIOT: Refunds"],
                    old_tag_xmlid,
                ],
            )

    # Migrate tag_diot_ret:
    # The tags needs to be mapped and to move from the base to the tax account.move.line
    # We will delete all lines with the old tags and add the tag to all lines that have
    # the tax origin.

    cr.execute(
        """
        INSERT INTO account_account_tag_account_move_line_rel (
                account_move_line_id,
                account_account_tag_id
            )
            SELECT aml.id,
                   CASE WHEN aml.debit > 0 THEN %s ELSE %s END
              FROM account_move_line aml
              JOIN l10n_mx_tax_id_with_tag_diot_ret diot
                ON diot.id = aml.tax_line_id
        """,
        [
            map_tags_name_to_id["-DIOT: Retención"],
            map_tags_name_to_id["+DIOT: Retención"],
        ],
    )

    # Drop temporary migration tables.
    cr.execute("DROP TABLE l10n_mx_aml_with_tags_to_replace")
    cr.execute("DROP TABLE l10n_mx_tax_id_with_tag_diot_ret")
