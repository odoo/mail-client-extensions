# -*- coding: utf-8 -*-
from textwrap import dedent
from openerp.addons.base.maintenance.migrations import util

def _db_origenip(cr, version):
    arch = dedent("""
        <?xml version="1.0"?>
        <data inherit_id="website_portal.portal_layout">
          <xpath expr="//div[@t-field=user.partner_id]" postion="attributes"
            <attribute name="t-options">{"widget": "contact", "fields": ["email", "phone", "address"]}</attribute>
          </xpath>
          <xpath expr="//div[@t-field=user.partner_id]" postion="before">
            <div t-field="user.partner_id.name"/>
            <div>Customer Number: AID<span t-esc="user.partner_id.id"/></div>
          </xpath>
        </data>
    """)
    cr.execute("UPDATE ir_ui_view SET arch_db=%s, inherit_id=%s WHERE id=2389",
               [arch, util.ref(cr, 'website_portal.portal_layout')])

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '1fc2da31-468a-4812-a8b9-feb9229a9a8d': _db_origenip,
    })
