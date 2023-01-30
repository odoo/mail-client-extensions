# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE project_project
           SET allow_billable = TRUE
         WHERE partner_id IS NOT NULL
           AND allow_billable IS NOT TRUE
        """
    )
