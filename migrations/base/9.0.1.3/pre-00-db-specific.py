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

    util.update_field_references(cr, 'seller_id', 'seller_ids',
                                 ('product.template', 'product.product'))

def _apps(cr, version):
    cr.execute("DELETE FROM ir_translation WHERE lang IN ('bs_BS', 'ur_PK')")
    cr.execute("UPDATE res_lang SET code='bs_BA', iso_code='bs_BA' WHERE code='bs_BS'")
    cr.execute("DELETE FROM res_lang WHERE code='ur_PK'")

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
    })
