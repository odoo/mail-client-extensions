# -*- coding: utf-8 -*-
from lxml import etree
from odoo.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    # 6.1 -> 7.0 left-overs
    util.remove_model(cr, 'account.followup.print')
    util.remove_model(cr, 'account.coda.trans.category')
    cr.execute("DELETE FROM ir_model_fields WHERE model='ir.actions.url'")

    util.remove_view(cr, 'openerp_website.website_data-selectors')
    cr.execute("UPDATE ir_ui_view SET active=false WHERE id=10821")

    # do not need to be changed
    util.force_noupdate(cr, 'sale_subscription.email_subscription_open', True)
    # waiting revert in saas~11.2
    util.force_noupdate(cr, 'openerp_enterprise.reminder_expiration_one_app_free_email', True)

    with util.edit_view(cr, view_id=8118) as view:
        button = view.find('button')
        button.attrib['position'] = 'attributes'
        del button[0]
        button.append(etree.fromstring(
            """<attribute name='context'>{'project_id': project_id, 'name': name, 'partner_id': partner_id,
                  'default_x_owner_id' : user_id, 'default_reviewer_id': reviewer_id,
                  'default_sale_line_id': sale_line_id, 'default_mnt_subscription_id': mnt_subscription_id}
            </attribute>"""
        ))
        button.append(etree.fromstring('<attribute name="groups"></attribute>'))

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
