# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # create an empty template to satisfy the mandatory field after migration
    env = util.env(cr)
    if env['sale.subscription'].search_count([('template_id', '=', False), ('type', '=', 'contract')]):
        default = env['sale.subscription'].create({
            'type': 'template',
            'name': 'Default Template',
            'reference': 'DEF',
            'state': 'open',
            'description': 'This empty template is here to enforce the mandatory template on subscriptions and was created automatically when you switched to Odoo 9. Feel free to replace it with something more meaningful to your business.'
        })
        cr.execute("""
            UPDATE sale_subscription SET
                template_id = %s
                WHERE template_id IS NULL""" % default.id)
