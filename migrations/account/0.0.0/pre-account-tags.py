# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
              SELECT at.account_account_tag_id, account.chart_template_id, ARRAY_AGG(account.code)
                FROM account_account_template_account_tag at
                JOIN account_account_template account ON at.account_account_template_id = account.id
            GROUP BY at.account_account_tag_id, account.chart_template_id
            ORDER BY at.account_account_tag_id
        """
    )
    util.ENVIRON["account_tags_pre_config"] = cr.fetchall()
