# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    for name in {"rating", "conversations", "response"}:
        util.create_column(cr, "digest_digest", f"kpi_livechat_{name}", "boolean")
