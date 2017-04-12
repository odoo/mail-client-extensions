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

def _db_plantadvancesa(cr, version):
    util.remove_view(cr, '__custo__.hr_expense_qweb_plant')
    cr.execute("UPDATE hr_expense SET reference = x_ref")
    cr.execute("""
        UPDATE hr_expense_sheet s
           SET responsible_id = e.x_user_valid_id
          FROM hr_expense e
         WHERE e.sheet_id = s.id
    """)
    util.remove_field(cr, 'hr.expense', 'x_ref')
    util.remove_field(cr, 'hr.expense', 'x_user_valid_id')

    arch = dedent("""
        <field name="tax_ids" position="before">
          <field name="x_partner_ids" widget="many2many_tags"/>
        </field>
    """)
    cr.execute("UPDATE ir_ui_view SET arch_db=%s WHERE id=2356", [arch])
    util.env(cr)['ir.ui.view'].create({
        'name': 'hr.expense.sheet.custo.mig',
        'model': 'hr.expense.sheet',
        'mode': 'extension',
        'inherit_id': util.ref(cr, 'hr_expense.view_hr_expense_sheet_form'),
        'arch': """
            <field name='responsible_id' position='attributes'>
                <attribute name='invisible'>0</attribute>
            </field>
        """
    })
    with util.edit_view(cr, view_id=1823) as arch:
        node = arch.xpath('//xpath[last()]')[0]
        node.attrib['expr'] = "//button[@name='action_invoice_open']"

def _db_live(cr, version):      # aka bodybuildpro
    util.remove_view(cr, view_id=1807)

def _db_scratchmusicgroup(cr, version):
    with util.edit_view(cr, view_id=1137) as arch:
        arch.attrib['name'] = 'action_invoice_open'


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '1fc2da31-468a-4812-a8b9-feb9229a9a8d': _db_origenip,
        '4a0cd30d-ac94-4769-9e1e-21d8279c7870': _db_plantadvancesa,
        'e4fc0190-6b16-4547-a427-e175b11ecbd3': _db_live,
        '7f28f9fe-bd35-4df2-8dc9-906577375e43': _db_scratchmusicgroup,
    })
