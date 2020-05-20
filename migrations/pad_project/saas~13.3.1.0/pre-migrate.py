# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_project", "pad_availability", "varchar")
    cr.execute(
        """
        UPDATE project_project
           SET pad_availability = CASE WHEN privacy_visibility = 'portal' AND use_pads THEN 'portal'
                                       ELSE 'internal'
                                   END
        """
    )
