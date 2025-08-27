import re

from odoo.upgrade import util

account = util.import_script("account/saas~18.5.1.4/pre-remove-tax-tag-invert.py")


def migrate(cr, version):
    # update move line tags for reverse charge
    cr.execute_values(
        """
        UPDATE account_account_tag_account_move_line_rel tag_aml_rel
           SET account_account_tag_id = target_tag.id
          FROM (VALUES %s) AS faulty_data(xmlid_re, source_tag, target_tag),
               account_move_line source_line
          JOIN account_move_line_account_tax_rel tax_rel
            ON tax_rel.account_move_line_id = source_line.id
          JOIN ir_model_data tax_imd
            ON tax_imd.res_id = tax_rel.account_tax_id
           AND tax_imd.model = 'account.tax'
           AND tax_imd.module = 'account',
               account_account_tag source_tag,
               account_account_tag target_tag
         WHERE tag_aml_rel.account_move_line_id = source_line.id
           AND tag_aml_rel.account_account_tag_id = source_tag.id
           AND tax_imd.name ~ faulty_data.xmlid_re
           AND source_tag.name ->> 'en_US' = faulty_data.source_tag
           AND target_tag.name ->> 'en_US' = faulty_data.target_tag
           AND source_tag.country_id = target_tag.country_id
        """,
        [
            (rf"^\d+_{re.escape(xmlid)}$", source_tag, target_tag)
            for xmlid, source_tag, target_tag in account.REVERSE_CHARGE_TAGS
        ],
    )
    # update tax config tags for reverse charge
    cr.execute_values(
        """
        UPDATE account_account_tag_account_tax_repartition_line_rel tag_tax_rel
           SET account_account_tag_id = target_tag.id
          FROM (VALUES %s) AS faulty_data(xmlid_re, source_tag, target_tag),
               account_tax_repartition_line repartition
          JOIN ir_model_data tax_imd
            ON tax_imd.res_id = repartition.tax_id
           AND tax_imd.model = 'account.tax'
           AND tax_imd.module = 'account',
               account_account_tag source_tag,
               account_account_tag target_tag
         WHERE tag_tax_rel.account_tax_repartition_line_id = repartition.id
           AND tag_tax_rel.account_account_tag_id = source_tag.id
           AND tax_imd.name ~ faulty_data.xmlid_re
           AND source_tag.name ->> 'en_US' = faulty_data.source_tag
           AND target_tag.name ->> 'en_US' = faulty_data.target_tag
           AND source_tag.country_id = target_tag.country_id
        """,
        [
            (rf"^\d+_{re.escape(xmlid)}$", source_tag, target_tag)
            for xmlid, source_tag, target_tag in account.REVERSE_CHARGE_TAGS
        ],
    )

    cr.execute("DROP TABLE _upg_to_create_aml")
    cr.execute("DROP TABLE _upg_tag_pairs")
