# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        WITH icp AS (
           DELETE FROM ir_config_parameter
                 WHERE key = 'account_reports.assets_report.groupby_prefix_groups_threshold'
             RETURNING value::NUMERIC AS threshold
        )
        UPDATE account_report ar
           SET prefix_groups_threshold = icp.threshold
          FROM icp
         WHERE ar.id = %s
    """,
        [(util.ref(cr, "account_asset.assets_report"),)],
    )
