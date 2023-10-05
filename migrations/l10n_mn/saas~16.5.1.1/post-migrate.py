# The test for this script is found under l10n_mn_reports/tests/test_vat_report_16_5.py
# as it requires l10n_mn_reports to be installed prior to the upgrade.

import json

from odoo import SUPERUSER_ID, api


def migrate_tags_to_tax_tags_engine(cr, module, tax_tag_changes):
    """Helper to perform the migration of tax tags when migrating a tax report
    from using domain formulas to tax_tags formulas.

    Typically, when using domain formulas, the tax tags are defined explicitly
    in the module data. This is not the case for tax tags created by the
    tax_tags engine, which are dynamically created when loading the tax report.

    A problem occurs when migrating a tax report from domain formulas to
    tax_tags formulas, which is that for each old tax tag, there are two new
    ones, a '+' tag and a '-' tag. The tax tags on AMLs need to be changed
    from the old ones to the appropriate new ones.

    This function performs this conversion, using the following rationale:

    Using a domain formula, the value of an expression is the sum or -sum of
    (AML.balance) over a domain [('tax_tag_ids', '=', tax_tag)].

    When converted to the tax tags engine, its value is the sum of
    (AML.balance) * (tax tag sign) * (-1 if AML.tax_tag_invert else 1).

    To keep the sum the same, we choose the appropriate new tag (+ or -) on
    each AML, depending on whether the expression was previously a + or -sum,
    and on whether AML.tax_tag_invert is set.

    This function should be used in the post-migrate script (after the
    new tax report has been loaded and the new tax tags have been created).

    :param module: the name of the module that defined the old tax tags
    :param tax_tag_changes: a dict {old_tax_tag_xmlid: (new_tag_name, "+" or "-")}
                            that for each old tax tag xmlid (without the module name), gives:
                                the name of the new tag, and
                                "+" if the old report line was doing a +sum, else "-"
    :raises KeyError: if, for any of the old tags, the corresponding new + or - tag
                      cannot be found.
    """
    cr.execute(
        """
        SELECT res_id, name
          FROM ir_model_data
         WHERE module = %s
               AND model = 'account.account.tag'
               AND name IN %s
        """,
        [module, tuple(tax_tag_changes)],
    )
    old_tags = cr.fetchall()

    old_tag_ids = [id for id, name in old_tags]
    old_minus_sum_tag_ids = [id for id, name in old_tags if tax_tag_changes[name][1] == "-"]

    cr.execute(
        """
          SELECT id, name->>'en_US', tax_negate
            FROM account_account_tag
           WHERE SUBSTRING(name->>'en_US', 2, LENGTH(name->>'en_US') - 1) IN %s
        """,
        [tuple(info[0] for info in tax_tag_changes.values())],
    )
    new_tags = cr.fetchall()

    new_plus_tag_ids_by_name = {name[1:]: id for id, name, tax_negate in new_tags if not tax_negate}
    new_minus_tag_ids_by_name = {name[1:]: id for id, name, tax_negate in new_tags if tax_negate}
    # mapping "old tag id" -> new '+' tag id
    plus_tag_mapping_json = json.dumps(
        {id: new_plus_tag_ids_by_name[tax_tag_changes[name][0]] for id, name in old_tags}
    )
    # mapping "old tag id" -> new '-' tag id
    minus_tag_mapping_json = json.dumps(
        {id: new_minus_tag_ids_by_name[tax_tag_changes[name][0]] for id, name in old_tags}
    )

    cr.execute(
        """
        UPDATE account_account_tag_account_move_line_rel tag_aml_rel
           SET account_account_tag_id =
               CASE
                   WHEN ( -- AML not inverted and we want the report line to give a +sum -> +tag
                        NOT account_move_line.tax_tag_invert AND tag_aml_rel.account_account_tag_id NOT IN %(minus_sum_tags)s
                          -- AML inverted and we want the report line to give a -sum -> +tag
                        OR account_move_line.tax_tag_invert AND tag_aml_rel.account_account_tag_id IN %(minus_sum_tags)s
                   )
                   THEN (%(plus_map)s::jsonb->>tag_aml_rel.account_account_tag_id::text)::int
                   -- otherwise -> -tag
                   ELSE (%(minus_map)s::jsonb->>tag_aml_rel.account_account_tag_id::text)::int
               END
          FROM account_move_line
         WHERE tag_aml_rel.account_account_tag_id IN %(all_tags)s
               AND account_move_line.id = tag_aml_rel.account_move_line_id
        """,
        {
            "minus_sum_tags": tuple(old_minus_sum_tag_ids),
            "plus_map": plus_tag_mapping_json,
            "minus_map": minus_tag_mapping_json,
            "all_tags": tuple(old_tag_ids),
        },
    )


def migrate(cr, version):
    """Handle the migration of the VAT report."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    # The VAT report tax tags have been changed.
    # For each old tax tag, the following dict indicates:
    #   - which new tag should replace it on AMLs (with the +/- prefix determined separately)
    #   - whether it was applicable to base lines (so should be removed from tax lines)
    #       or to tax lines (so should be removed from base lines).
    #       This is because some tax tags used to be set on both base lines and tax lines,
    #       and were distinguished in the old report using domains like
    #       ('tax_line_id', '!=', False) and ('tax_id', '!=', False)
    #   - whether the tax report line formula was a +sum or -sum of AML balances
    #       (necessary for determining which of the +- tags we should put on each AML)

    tax_tag_changes = {
        # Old tag:         (New tag, Was the formula a +/- sum?, base or tax?)
        "vat_report_tag2": ("TT3a[2]", "-", "base"),
        "vat_report_tag5": ("TT3a[5]", "-", "base"),
        "vat_report_tag6": ("TT3a[6]", "-", "base"),
        "vat_report_tag7": ("TT3a[7]", "-", "base"),
        "vat_report_tag8": ("TT3a[8]", "-", "base"),
        "vat_report_tag9": ("TT3a[9]", "-", "base"),
        "vat_report_tag11": ("TT3a[24]", "-", "base"),
        "vat_report_tag12": ("TT3a[11]", "-", "base"),
        "vat_report_tag13": ("TT3a[12]", "-", "base"),
        "vat_report_tag14": ("TT3a[13]", "-", "base"),
        "vat_report_tag15": ("TT3a[14]", "-", "base"),
        "vat_report_tag16": ("TT3a[15]", "-", "base"),
        "vat_report_tag17": ("TT3a[16]", "-", "base"),
        "vat_report_tag18": ("TT3a[17]", "-", "base"),
        "vat_report_tag19": ("TT3a[18]", "-", "base"),
        "vat_report_tag20": ("TT3a[19]", "-", "base"),
        "vat_report_tag21": ("TT3a[20]", "-", "base"),
        "vat_report_tag22": ("TT3a[21]", "-", "base"),
        "vat_report_tag23": ("TT3a[22]", "-", "base"),
        "vat_report_tag24": ("TT3a[23]", "-", "base"),
        "vat_report_tag25": ("TT3a[24]", "-", "base"),
        "vat_report_tag28": ("TT3a[27]", "-", "base"),
        "vat_report_tag29": ("TT3a[28]", "-", "base"),
        "vat_report_tag33": ("TT3a[32]", "+", "base"),
        "vat_report_tag35": ("TT3a[34]", "+", "base"),
        "vat_report_tag36": ("TT3a[35]", "+", "base"),
        "vat_report_tag37": ("TT3a[36]", "+", "base"),
        "vat_report_tag37a": ("TT3a[37]", "+", "base"),
        "vat_report_tag37b": ("TT3a[38]", "+", "base"),
        "vat_report_tag37c": ("TT3a[39]", "+", "base"),
        "vat_report_tag37d": ("TT3a[40]", "+", "base"),
        "vat_report_tag38": ("TT3a[41]", "+", "base"),
        "vat_report_tag41": ("TT3a[44]", "+", "tax"),
        "vat_report_tag42": ("TT3a[45]", "+", "tax"),
        # vat_report_tag43: removed
        "vat_report_tag44": ("TT3a[46]", "+", "tax"),
        "vat_report_tag45": ("TT3a[47]", "+", "tax"),
        "vat_report_tag46": ("TT3a[48]", "+", "tax"),
        "vat_report_tag48": ("TT3a[50]", "-", "base"),
        "vat_report_tag49": ("TT3a[51]", "-", "base"),
        "vat_report_tag51": ("TT3a[53]", "+", "base"),
        "vat_report_tag52": ("TT3a[54]", "+", "base"),
        "vat_report_tag56a": ("TT3a[58]", "+", "base"),
        "vat_report_tag57a": ("TT3a[59]", "+", "tax"),
        "vat_report_tag58a": ("TT3a[60]", "-", "base"),
        "vat_report_tag59a": ("TT3a[61]", "-", "tax"),
    }

    # STEP 1: Unset tax tags on base lines / tax lines that shouldn't be there.
    #   In the previous version of the taxes, the same tax tags were being set both
    #   on base lines and tax lines. We need to remove the unwanted tags to avoid
    #   confusing the tax_tags engine.
    cr.execute(
        """
        SELECT res_id, name
          FROM ir_model_data
         WHERE module = 'l10n_mn'
               AND model = 'account.account.tag'
               AND name IN %s
        """,
        [tuple(tax_tag_changes)],
    )
    old_tags = cr.fetchall()

    old_tag_ids = [id for id, name in old_tags]
    old_tag_ids_for_base_lines = [id for id, name in old_tags if tax_tag_changes[name][2] == "base"]
    old_tag_ids_for_tax_lines = [id for id, name in old_tags if tax_tag_changes[name][2] == "tax"]

    cr.execute(
        """
        DELETE FROM account_account_tag_account_move_line_rel tag_aml_rel
              USING account_move_line aml
          LEFT JOIN account_move_line_account_tax_rel amlatr
                 ON amlatr.account_move_line_id = aml.id
              WHERE aml.id = tag_aml_rel.account_move_line_id
                    AND (
                        tag_aml_rel.account_account_tag_id IN %s
                        AND aml.tax_line_id IS NOT NULL
                      OR
                        tag_aml_rel.account_account_tag_id IN %s
                        AND amlatr.account_move_line_id IS NOT NULL
                    )

        """,
        [tuple(old_tag_ids_for_base_lines), tuple(old_tag_ids_for_tax_lines)],
    )

    # STEP 2: Change the VAT tags on AMLs, choosing the +tag or -tag where appropriate.
    migrate_tags_to_tax_tags_engine(cr, "l10n_mn", tax_tag_changes)

    # STEP 3: Remove the old VAT tags from repartition lines
    cr.execute(
        """
        DELETE FROM account_account_tag_account_tax_repartition_line_rel
              WHERE account_account_tag_id IN %s
        """,
        [tuple(old_tag_ids)],
    )

    # STEP 4: Reload CoA:
    # - will update all taxes with the new tax repartition lines on templates.
    # - will create new accounts if needed
    # - will set the Cashflow Statement tags on accounts
    for company in env["res.company"].search([("chart_template", "=", "mn")]):
        env["account.chart.template"].try_loading("mn", company=company, install_demo=False)
