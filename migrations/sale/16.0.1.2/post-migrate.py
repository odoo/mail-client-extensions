# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    changes = [
        ("acquirer_id", "provider_id"),
        ("tx.provider", "tx.provider_code"),
        ("token_id.name", "token_id.display_name"),
    ]
    for old, new in changes:
        util.replace_in_all_jsonb_values(
            cr, "mail_template", "body_html", old, new, extra_filter="t.model='sale.order'"
        )
