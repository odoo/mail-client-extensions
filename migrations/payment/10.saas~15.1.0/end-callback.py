# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    domain = [
        ('callback_model_id', '!=', False),
        ('callback_res_id', '!=', False),
        ('callback_method', '!=', False),
        ('callback_hash', '=', False),
    ]
    for tx in util.env(cr)['payment.transaction'].with_context(active_test=False).search(domain):
        tx.write({'callback_hash': tx._generate_callback_hash()})

    util.remove_field(cr, 'payment.transaction', 'callback_eval')
