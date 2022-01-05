# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # bundles
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            r"""
            DELETE FROM ir_attachment
                  WHERE res_model = 'ir.ui.view'
                    AND COALESCE(res_id, 0) = 0
                    AND res_field IS NULL
                    AND mimetype IN ('text/css', 'application/javascript')
                    AND url ~ '^/web/(content|assets)/\d+-[0-9a-f]+/.*\.(css|js)$'
            """,
            table="ir_attachment",
        ),
    )
    # individual css files
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            r"""
            DELETE FROM ir_attachment
                  WHERE res_model IS NULL
                    AND COALESCE(res_id, 0) = 0
                    AND res_field IS NULL
                    AND mimetype = 'text/css'
                    AND url ~ '^/[\w_]+/static/.*\.(scss|less|sass).css$'
            """,
            table="ir_attachment",
        ),
    )
