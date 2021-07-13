# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Add OSS tag to every OSS tax we find
    oss_tag_id = util.ref(cr, "l10n_eu_oss.tag_oss")
    cr.execute(
        """
        INSERT INTO account_account_tag_account_tax_repartition_line_rel(account_tax_repartition_line_id, account_account_tag_id)
            SELECT tax_rep_ln.id, %s
            FROM ir_model_data
            JOIN account_tax tax
                ON ir_model_data.model = 'account.tax.group' AND tax.tax_group_id = ir_model_data.res_id
            JOIN account_tax_repartition_line tax_rep_ln
                ON tax_rep_ln.invoice_tax_id = tax.id OR tax_rep_ln.refund_tax_id = tax.id
            WHERE
                ir_model_data.module = 'l10n_eu_oss'
    """,
        [oss_tag_id],
    )

    util.add_to_migration_reports(
        "OSS report is now available. By default, all your products are considered as originating from EU. "
        "In case some need to follow the IOSS regime, you'll need to set the 'non-EU origin' tag in their "
        "'Account Tags' field. Your history is unchanged and only future entries will be added to the report. "
        "If you have an open period and wish to also include some existing entries, you'll have "
        "to edit their tax grids accordingly.",
        "Tax configuration",
    )
