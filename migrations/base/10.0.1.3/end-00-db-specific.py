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

def _megamanhk(cr, version):
    util.env(cr)['ir.model.fields'].create({
        'name': 'x_phone',
        'field_description': 'Phone',
        'model': 'project.issue',
        'model_id': util.ref(cr, 'project_issue.model_project_issue'),
        'ttype': 'char',
        'store': False,
        'related': 'partner_id.phone',
        'state': 'manual'
    })
    cr.execute("""UPDATE ir_ui_view SET active=TRUE WHERE id=794;""")
    util.env(cr)['ir.ui.view'].create({
        'name': 'project.issue.form.custom',
        'model': 'project.issue',
        'priority': 99,
        'mode': 'extension',
        'type': 'form',
        'inherit_id': util.ref(cr, 'project_issue.project_issue_form_view'),
        'arch': """
<data>
  <xpath expr="//field[@name='tag_ids']" position="before">
    <field name="create_date" readonly="1"/>
    <field name="date_deadline"/>
    <field name="x_claim_no"/>
    <field name="x_old_ref_no"/>
  </xpath>
  <xpath expr="//field[@name='partner_id']" position="after">
    <field name="x_phone"/>
  </xpath>
  <xpath expr="//page[@name='extra_info']" position="before">
    <page string="Information">
      <group>
        <field name="ref"/>
        <field name="x_Lot"/>
        <field name="x_QtyInstalled"/>
        <field name="x_QtyFailed"/>
        <field name="x_Ambient_Temp"/>
        <field name="x_Voltage_Supplied"/>
        <field name="x_Install_Date"/>
        <field name="x_Install_Height"/>
        <field name="x_Supply_Condition"/>
        <field name="x_Worked_Hours"/>
        <field name="x_Duty_Cycle"/>
      </group>
    </page>
  </xpath>
  <xpath expr="//field[@name='task_id']" position="replace"/>
  <xpath expr="//field[@name='user_id']" position="attributes">
      <attribute name="context">{'default_user_id': user_id}</attribute>
  </xpath>
</data>
        """
    })
    util.env(cr)['ir.ui.view'].create({
        'name': 'project.issue.search.custom',
        'model': 'project.issue',
        'priority': 99,
        'mode': 'extension',
        'type': 'search',
        'inherit_id': util.ref(cr, 'project_issue.view_project_issue_filter'),
        'arch': """
<xpath expr="//field[@name='id']" position="after">
  <field name="x_claim_no"/>
</xpath>
        """
    })

def _moebius(cr, version):
    cr.execute(""" DELETE FROM ir_ui_menu
                         WHERE parent_id IS NULL AND name IN ('Test', 'testvente'); """)
    cr.execute(""" UPDATE account_journal
                      SET sequence=2
                    WHERE id IN (3,4); """)
    cr.execute(""" UPDATE mail_channel_partner
                      SET is_minimized = FALSE; """)
    cr.execute(""" UPDATE project_project
                      SET active=TRUE; """)
    cr.execute(""" UPDATE project_task
                      SET active=TRUE; """)
    cr.execute(""" DELETE FROM ir_ui_view_custom; """)
    cr.execute(""" INSERT INTO ir_ui_menu (name, sequence, active, parent_id, action)
                   SELECT 'Imprimer Sales/Purchases Journal' AS name,
                          99 AS sequence,
                          TRUE,
                          imd1.res_id,
                          imd2.model || ',' || imd2.res_id AS action
                     FROM ir_model_data imd1,
                          ir_model_data imd2
                    WHERE imd1.module='account'
                      AND imd1.name='menu_finance_reports'
                      AND imd2.module='account'
                      AND imd2.name='action_account_print_journal_menu'; """)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '1fc2da31-468a-4812-a8b9-feb9229a9a8d': _db_origenip,
        '4a0cd30d-ac94-4769-9e1e-21d8279c7870': _db_plantadvancesa,
        'e4fc0190-6b16-4547-a427-e175b11ecbd3': _db_live,
        '7f28f9fe-bd35-4df2-8dc9-906577375e43': _db_scratchmusicgroup,
        '16a70f1b-893a-4411-aa2a-d939171fac7d': _megamanhk,
        '2c03b0fe-1bc2-42ed-be3e-d2c9ec056839': _moebius,
    })
