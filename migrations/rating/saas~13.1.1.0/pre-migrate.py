# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "rating_rating", "is_internal", "boolean")
    cr.execute("""
        UPDATE rating_rating r
           SET is_internal = m.is_internal
          FROM mail_message m
         WHERE m.id = r.message_id
    """)

    cr.execute("""
        UPDATE ir_model_access
           SET perm_read = false, perm_write = false, perm_create = false, perm_unlink = false
         WHERE id IN %s
    """, [tuple(util.ref(cr, f"rating.access_rating_{group}") for group in {"public", "portal"})])
