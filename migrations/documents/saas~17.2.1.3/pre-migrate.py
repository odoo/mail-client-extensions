# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "documents_share", "allow_upload", "boolean")
    util.explode_execute(
        cr,
        "UPDATE documents_share SET allow_upload = TRUE WHERE action = 'downloadupload'",
        table="documents_share",
    )
    util.remove_field(cr, "documents.share", "action")
