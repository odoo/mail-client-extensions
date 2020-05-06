# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    The goal of this script is to clean some customisation that have been
    encountered several times instead of creating multiple specific scripts.
    """

    if util.table_exists(cr, "dev_export_fields"):
        cr.execute(
            """
                ALTER TABLE dev_export_fields
            DROP CONSTRAINT dev_export_fields_name_fkey,
             ADD CONSTRAINT dev_export_fields_name_fkey FOREIGN KEY (name)
                 REFERENCES ir_model_fields(id) ON DELETE CASCADE
            """
        )
