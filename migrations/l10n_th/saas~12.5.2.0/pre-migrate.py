# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Create temporary map table for tax report tag
    cr.execute(
        """
        CREATE TABLE  l10n_th_new_tax_report_tag_map(
            old_tax_report_line_xml_ref VARCHAR,
            old_tax_report_line_id INTEGER,
            old_plus_tag_id INTEGER,
            old_minus_tag_id INTEGER,
            new_tax_report_line_xml_ref VARCHAR,
            new_tax_report_line_id INTEGER,
            new_plus_tag_id INTEGER,
            new_minus_tag_id INTEGER
            );
    """
    )
    # Add Tax report lines in temporary map table
    cr.execute(
        """
        INSERT INTO l10n_th_new_tax_report_tag_map(old_tax_report_line_xml_ref, old_tax_report_line_id)
            SELECT ir_md.name, atrl.id
            FROM account_tax_report_line atrl
            JOIN ir_model_data ir_md ON res_id = atrl.id and model = 'account.tax.report.line'
            WHERE atrl.tag_name IS NOT NULL
    """
    )

    # Update plus tags related to tax report line
    cr.execute(
        """
        UPDATE l10n_th_new_tax_report_tag_map trm
            SET old_plus_tag_id = tag.id
        FROM account_tax_report_line_tags_rel atrl_tag
        JOIN account_account_tag tag ON tag.id = atrl_tag.account_account_tag_id
        WHERE atrl_tag.account_tax_report_line_id = trm.old_tax_report_line_id and tag.tax_negate != true
    """
    )

    # Update minus tags related to tax report line
    cr.execute(
        """
        UPDATE l10n_th_new_tax_report_tag_map trm
            SET old_minus_tag_id = tag.id
        FROM account_tax_report_line_tags_rel atrl_tag
        JOIN account_account_tag tag ON tag.id = atrl_tag.account_account_tag_id
        WHERE atrl_tag.account_tax_report_line_id = trm.old_tax_report_line_id and tag.tax_negate = true
    """
    )

    cr.execute(
        """
        SELECT name
          FROM ir_model_data
         WHERE module = 'l10n_th'
           AND model = 'account.tax.report.line'
    """
    )
    for name in cr.fetchall():
        util.remove_record(cr, "l10n_th." + name[0])

    util.delete_unused(cr, "l10n_th.tax_group_7")
    util.delete_unused(cr, "l10n_th.acc_type_other")
