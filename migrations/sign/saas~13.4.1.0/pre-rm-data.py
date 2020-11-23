# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "sign.sign_template_with_archived_action")

    # remove data moved to demo
    cr.execute("SELECT demo FROM ir_module_module WHERE name = 'sign'")
    [demo] = cr.fetchone()
    if not demo:
        for item in [1, 2, 3, 4, 5, 8, 9, 20, 21, 22, 23, 24, 25]:
            util.delete_unused(cr, f"sign.sign_item_{item}")
        for id_ in [1, 3]:
            util.delete_unused(cr, f"sign.template_sign_{id_}")
            if util.ref(cr, f"sign.template_sign_{id_}"):
                util.force_noupdate(cr, f"sign.attachment_sign_{id_}", True)
            else:
                util.remove_record(cr, f"sign.attachment_sign_{id_}")
