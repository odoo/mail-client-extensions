# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "approval_category", "active", "boolean")
    cr.execute(
        """
        ALTER TABLE approval_category
       ALTER COLUMN requirer_document
               TYPE varchar
              USING CASE WHEN requirer_document THEN 'required' ELSE 'optional' END
    """
    )
    cr.execute("UPDATE approval_category SET active = true")
