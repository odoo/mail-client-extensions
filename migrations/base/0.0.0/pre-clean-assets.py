# -*- coding: utf-8 -*-


def migrate(cr, version):
    # bundles
    cr.execute(
        r"""
            DELETE FROM ir_attachment
                  WHERE res_model = 'ir.ui.view'
                    AND COALESCE(res_id, 0) = 0
                    AND res_field IS NULL
                    AND mimetype IN ('text/css', 'application/javascript')
                    AND url ~ '^/web/(content|assets)/\d+-[0-9a-f]+/.*\.(css|js)$'
                    AND url LIKE '%assets%'
    """
    )
    # individual css files
    cr.execute(
        r"""
            DELETE FROM ir_attachment
                  WHERE res_model IS NULL
                    AND COALESCE(res_id, 0) = 0
                    AND res_field IS NULL
                    AND mimetype = 'text/css'
                    AND url ~ '^/[\w_]+/static/.*\.(scss|less|sass).css$'
        """
    )
