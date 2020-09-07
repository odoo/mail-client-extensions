# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.replace_record_references(
        cr,
        ("payment.acquirer", util.ref(cr, "payment.payment_acquirer_custom")),
        ("payment.acquirer", util.ref(cr, "payment.payment_acquirer_transfer")),
        replace_xmlid=False,
    )
    util.remove_record(cr, "payment.payment_acquirer_custom")
