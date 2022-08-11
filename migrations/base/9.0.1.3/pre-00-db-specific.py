# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    util.merge_module(cr, 'sale_contract', 'account_analytic_analysis')
    cr.execute("DELETE FROM ir_model_data WHERE module='base' and name='module_sale_contract'")
    cr.execute("UPDATE account_analytic_account SET recurring_invoices='t' WHERE contract_type='subscription'")

    cr.execute("""
        DELETE FROM openerp_enterprise_database_app
              WHERE module_id IN (SELECT id
                                    FROM ir_module_module
                                   WHERE name IN ('contacts', 'hr_applicant_document', 'im_chat')
                                 )
    """)

    # we have some invoices with incorrect type so we must correct them first
    cr.execute("""UPDATE account_invoice set type='out_refund' WHERE type = 'out_invoice' AND journal_id in (12, 15, 16)""")

    # theses records have already been deleted in prod database, but local copies may still have them
    cr.execute("DELETE FROM account_tax WHERE id IN (1377, 1379, 1380, 1381)")
    cr.execute("ALTER TABLE account_analytic_line ALTER COLUMN general_account_id DROP NOT NULL")
    cr.execute("UPDATE account_analytic_line SET general_account_id=NULL WHERE id=1525")

    # remove old inherited views
    for view in [2274, 2318, 7336, 7361, 7437, 7443, 7743, 8225, 8226]:
        util.remove_view(cr, view_id=view, silent=True)
    util.remove_view(cr, 'openerp_payment.view_partners_form_payment_defaultcreditcard')
    util.remove_view(cr, 'openerp_enterprise.view_partners_form_plan')
    util.force_noupdate(cr, 'openerp_enterprise.view_customer_invoice_lines_popup', False)

    with util.edit_view(cr, view_id=8183) as arch:
        bad = arch.find('.//xpath')
        bad.getparent().remove(bad)

    cr.execute("DELETE FROM ir_filters WHERE id=11151")
    cr.execute("DELETE FROM ir_rule WHERE id=260")
    # FORGOT HISTORY
    cr.execute("TRUNCATE im_chat_message")

    # fix some custom server actions
    cr.execute("UPDATE ir_act_server SET code=replace(code, 'message.type', 'message.message_type') WHERE id in (2265, 2378)")
    cr.execute("UPDATE ir_act_server SET code=replace(code, 'type', 'message_type') WHERE id=2278")


def _andrew(cr, version):
    # remove views inheriting deprecated view:
    views = (
        'stock.move.form.nel',
        'transfer.nel',
    )
    cr.execute("select id from ir_ui_view where name in %s", [views])

    for view_id, in cr.fetchall():
        util.remove_view(cr, view_id=view_id)

    # disable problematic views
    views = (
        'hr.nel',
        'statement.line.nel',
        'Asset.nel',
        'product.template.search.nel',
        'purchase.order.inherit_288',
    )
    cr.execute("UPDATE ir_ui_view SET active=false WHERE name IN %s", [views])

def _mckay(cr, version):
    util.remove_module(cr, 'statement_voucher_killer')

def _anc2systems(cr, version):
    cr.execute("DELETE FROM ir_values WHERE name='supplier_taxes_id' AND key='default'")

def _irisob(cr, version):
    for v in [1370, 1377, 1409, 1406, 1413]:
        util.remove_view(cr, view_id=v)
    cr.execute("DELETE FROM ir_act_window_view WHERE id=102")

    with util.skippable_cm(), util.edit_view(cr, 'sale.report_saleorder_document') as arch:
        node = arch.find('.//div[@class="page"]')
        util.lxml.etree.SubElement(node, 'p', id='fiscal_position_remark')

    with util.skippable_cm(), util.edit_view(cr, view_id=1035) as arch:
        node = arch.find('./field[@name="fiscal_position"]')
        node.attrib['name'] = 'fiscal_position_id'

    with util.skippable_cm(), util.edit_view(cr, view_id=1408) as arch:
        for node in arch.xpath('//field[@name="payment_term"]'):
            node.attrib['name'] = 'payment_term_id'

    with util.skippable_cm(), util.edit_view(cr, view_id=1045) as arch:
        node = arch.find('.//field[@name="minimum_planned_date"]')
        node.getparent().remove(node)

def _electronics123(cr, version):
    cr.execute("""
        INSERT INTO ir_model_fields(
            model, model_id, select_level, name, field_description, ttype, state, translate,
            readonly, selectable, required)
        VALUES('product.template', 180, 0, 'x_product_case', 'Case', 'char', 'manual', false,
               false, true, false);
    """)
    cr.execute("ALTER TABLE product_template RENAME loc_case TO x_product_case")

    # update view `report_picking_lah`
    with util.skippable_cm(), util.edit_view(cr, view_id=942) as arch:
        for x in arch.xpath('//xpath[contains(@expr, "[3]")]'):
            arch.remove(x)
        span = arch.find('.//span')
        span.attrib['t-field'] = 'pack_operation.product_id.loc_case'

    # and view `lah_product_form`
    cr.execute("UPDATE ir_ui_view SET arch_db=%s WHERE id=976", ["""
<data>
<group name="group_standard_price" position="inside">
  <field name="x_lah_amazon"/>
  <field name="x_rohs"/>
  <field name="x_skilllevel"/>
  <field name="x_datasheet"/>
</group>
<xpath expr="//group[@name='inventory']/group" position="inside">
  <field name="x_product_case"/>
</xpath>
</data>
    """])

    # and ... (you get it)
    with util.skippable_cm(), util.edit_view(cr, view_id=972) as arch:
        arch.attrib['expr'] = "//field[@name='property_account_position_id']"

    util.update_field_references(cr, 'seller_id', 'seller_ids',
                                 ('product.template', 'product.product'))
    cr.execute('''update ir_ui_view set arch_db=replace(arch_db,'loc_case','x_product_case') where id=1343;''')

def _apps(cr, version):
    cr.execute("DELETE FROM ir_translation WHERE lang IN ('bs_BS', 'ur_PK')")
    cr.execute("UPDATE res_lang SET code='bs_BA', iso_code='bs_BA' WHERE code='bs_BS'")
    cr.execute("DELETE FROM res_lang WHERE code='ur_PK'")

def _duck_food(cr, version):
    cr.execute(""" update ir_ui_view set arch = '<xpath expr="//tree" position="attributes"><attribute name="toolbar"/></xpath>' where id=920; """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, '<filter string="Country" position="after">', '<group name="group_by" position="inside">') where id=830; """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, '</filter>', '</group>') where id=830; """)
    cr.execute(""" update ir_ui_view set active=false where id = 1036; """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, '<group string="Bank Accounts" position="after">', '<group name="account_grp" position="after">') where id=934; """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, '<group string="Group By"', '<xpath expr="//group[1]"') where id=1213; """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, '</group', '</xpath') where id=1213; """)
    cr.execute(""" update ir_ui_view set arch = regexp_replace(arch, '<button string="Transfer".*</button>', '<xpath expr="//button[@name=''do_new_transfer'']" position="attributes"><attribute name="groups">stock.group_stock_manager</attribute></xpath><xpath expr="//button[@name=''do_new_transfer'']" position="after"><button states="assigned,partially_available" string="Pallet Transfer" groups="stock.group_stock_user" type="action" name="703" class="oe_highlight"/></xpath>', 's') where id=974; """)
    cr.execute(""" update ir_ui_view set inherit_id=null where id = 1401; """)
    cr.execute(""" update ir_ui_view set inherit_id=null,mode='primary' where id  in (1355,1247,1147,821,1070,920); """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, 'line_id', 'line_ids') where id = 1268; """)
    cr.execute(""" update ir_ui_view set arch=regexp_replace(arch, '<xpath expr="//field\[@name=''journal_id.*</xpath>', '', 's') where id = 1268; """)
    cr.execute(""" delete from ir_ui_view where id in (1312,1425); """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, 'fiscal_position', 'fiscal_position_id') where id = 1293; """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, 'fiscal_position', 'fiscal_position_id') where id = 1167; """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, 'invoice_line', 'invoice_line_ids') where id = 1167; """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, '<field name="portal_payment_options" position="replace"/>', '') where id = 1167; """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, 'expr="//page[@string=''Payments'']" position="after"', 'expr="//notebook" position="inside"') where id=1062; """)
    cr.execute(""" update ir_ui_view set arch=regexp_replace(arch, '<field name="categ_id.*?</field>', '', 's') where id in (1054); """)
    cr.execute(""" update ir_ui_view set arch=replace(arch, 'categ_id', 'name') where id in (1054); """)
    cr.execute(""" update ir_ui_view set arch=regexp_replace(arch, '<field name="categ_id.*?</field>', '', 's') where id=1051; """)
    cr.execute(""" update ir_ui_view set arch=regexp_replace(arch, '<field name="loc_rack.*?</field>', '<group name="group_lots_and_weight" position="inside"><field name="x_pick_volgorde"/></group>', 's') where id=1051; """)
    cr.execute(""" delete from ir_ui_view where id in (1247,1355); """)
    cr.execute(""" update ir_ui_view set arch='<data><field name="phone" position="before"><field name="issued_total" sum="Overdue Amount"/></field></data>' where id=1260; """)
    cr.execute("""update ir_ui_view set active=false,mode='primary',model='sale.order',inherit_id=null where id=843""")
    cr.execute("""update ir_ui_view set arch=replace(arch, 'fiscal_position', 'fiscal_position_id') where id=843""")
    cr.execute("""update ir_ui_view set arch=replace(arch, 'payment_term', 'payment_term_id') where id=843""")
    cr.execute("""update ir_ui_view set arch=replace(arch, 'button name="cancel"', 'button name="action_cancel"') where id=843""")
    cr.execute("""update ir_ui_view set arch=regexp_replace(arch, '<button name="copy_quotation.*?</button>', '', 's') where id=843""")
    cr.execute("""update ir_ui_view set arch=replace(arch, '<field name="portal_payment_options" position="replace"/>','') where id=843""")
    cr.execute("""update ir_ui_view set arch=replace(arch, 'on_change="onchange_fiscal_position_id(fiscal_position_id, order_line, context)"', '') where id=843""")
    cr.execute("""update ir_ui_view set arch=replace(arch, 'on_change="onchange_partner_id(partner_id, context)"', '') where id=843""")
    cr.execute("""update ir_ui_view set arch=replace(arch, 'on_change="onchange_delivery_id(company_id, partner_id, partner_shipping_id, fiscal_position_id)"', '') where id=843""")


def _ephyla(cr, version):
    cr.execute(""" UPDATE ir_ui_view
        SET arch = replace(arch, 'property_account_position', 'property_account_position_id')
        WHERE id=1024; """)

def _icus(cr, version):
    cr.execute(""" UPDATE res_partner
                   SET title = NULL
                   WHERE title = 1; """)

def _metalpros(cr, version):
    # these f... ir_values prevent the creation of new products, by example when you import xml data
    cr.execute(""" delete from ir_values where id in (425,426) """)
    cr.execute("""delete from account_fiscal_position_tax_template""")
    cr.execute("""delete from account_tax_template where chart_template_id=3""")
    cr.execute("""delete from ir_ui_view where id=1684""")

def _moebius(cr, version):
    cr.execute(""" DELETE FROM ir_model_fields
                         WHERE model='sale.report' AND name='date_confirm'; """)
    cr.execute(""" UPDATE ir_filters
                      SET context = replace(context, 'date_confirm', 'date')
                    WHERE id=42; """)
    cr.execute(""" UPDATE account_tax
                      SET description = 'VAT-OUT-21-S'
                    WHERE name = 'VAT 21% - Services'; """)
    cr.execute(""" UPDATE account_tax t
                      SET name = att.name
                     FROM account_tax_template att
                    WHERE t.description = att.description AND t.name != att.name; """)

def _megamanhk(cr, version):
    util.force_install_module(cr, 'project_issue')

def _bunkerit(cr, version):
    with util.skippable_cm(), util.edit_view(cr, 'sale.report_saleorder_document') as arch:
        node = arch.find('.//div[@class="page"]')
        util.lxml.etree.SubElement(node, 'p', id='fiscal_position_remark')

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '05a64ced-5b98-488d-a833-a994f9b1dd80': _db_openerp,    # test
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,    # prod
        '0950c4ec-5bda-11e5-816e-002590a742c0': _andrew,        # andrew-alliance-sept
        '1231bd5a-4d59-11e3-80e6-f23c91dbe612': _andrew,        # andrew-alliance
        'bb7ddc42-1065-11e5-9445-b083fec18343': _mckay,
        '481d7a23-7e5e-4bf5-80bf-57e3ef74c435': _anc2systems,
        '9d923224-1dcf-4819-ae76-5079c2718598': _irisob,
        '885e1afc-694e-41c6-b496-a08d6a34c360': _electronics123,
        'a0a30d16-6095-11e2-9c70-002590a17fd8': _apps,
        '2b0cac2f-79f1-4a1c-8263-ada77758b100': _duck_food,
        '62f0a964-2e5e-47bb-be99-0a7579b0b27f': _ephyla,
        '058fa140-7b35-4150-8b2b-06b310a2b7b9': _icus,
        '8f4ad700-f69a-4ab3-b24a-4792c1f629f8': _metalpros,
        '2c03b0fe-1bc2-42ed-be3e-d2c9ec056839': _moebius,
        '16a70f1b-893a-4411-aa2a-d939171fac7d': _megamanhk,
        'c98c9b75-88e5-44c5-a203-11891f5adfef': _bunkerit,
    })
