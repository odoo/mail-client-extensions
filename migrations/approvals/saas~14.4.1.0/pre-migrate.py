# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    approval_type_id = util.ref(cr, "approvals.mail_activity_data_approval")
    cr.execute("UPDATE mail_activity_type SET active = false WHERE id = %s", [approval_type_id])
    util.convert_field_to_html(cr, "approval.request", "reason")
