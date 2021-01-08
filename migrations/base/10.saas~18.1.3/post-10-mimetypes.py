# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    cr.execute(
        """
            SELECT id, datas_fname
              FROM ir_attachment
             WHERE COALESCE(mimetype, '') = ''
        """
    )
    mimetypes = []
    for attachment_id, fname in cr.fetchall():
        mimetype = env["ir.attachment"]._compute_mimetype({"datas_fname": fname})
        mimetypes.append((mimetype, attachment_id))
    cr.executemany(
        """
            UPDATE ir_attachment
               SET mimetype = %s
             WHERE id = %s
        """,
        mimetypes,
    )
