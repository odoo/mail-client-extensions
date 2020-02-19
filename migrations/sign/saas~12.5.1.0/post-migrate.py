# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    cr.execute("select id,sign_request_id FROM sign_request_item_value where sign_request_item_id IS null")
    for res in cr.dictfetchall():
        new_sri = env["sign.request.item"].sudo().create({"sign_request_id": res["sign_request_id"]})
        cr.execute("UPDATE sign_request_item_value SET sign_request_item_id=%s WHERE id=%s", [new_sri.id, res["id"]])
    util.remove_column(cr, "sign_request_item_value", "sign_request_id")
    cr.execute("ALTER TABLE sign_request_item_value ALTER COLUMN sign_request_item_id SET NOT NULL")
