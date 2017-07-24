# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    # remove relation to module im_odoo_support
    cr.execute("DELETE FROM openerp_enterprise_database_app WHERE module_id = 444")

    # cleanup bad/duplicated attendance entries
    cr.execute("""
        DELETE FROM hr_attendance WHERE id IN (
            15152, 15153, 15154,            -- duplicated (no check_out)
            23479, 23483, 23898, 23899,     -- duplicated entries (same check_in date)
            1396, 10513, 12899,             -- extra check_in which generate overlaps
            10001                           -- extra check_in from jan 2012
        )
    """)
    util.remove_view(cr, 'openerp_website.openerp_editor_head')

def _boldom(cr, version):
    util.force_install_module(cr, 'helpdesk')

def _ngpinc(cr, version):
    cr.execute("""
        UPDATE ir_ui_view
           SET arch_db = '<?xml version="1.0"?>
<data>
  <xpath expr="//group/group" position="inside">
    <field name="x_notes"/>
  </xpath>
</data>'
         WHERE id=903
    """)
    cr.execute("UPDATE ir_ui_view SET mode='primary' WHERE id=403")
    cr.execute("""
        UPDATE ir_model_fields
           SET depends = 'product_id,procurement_group_id',
               compute = replace(compute, 'move_prod_id.', 'procurement_')
         WHERE id=5794
    """)

def _national_equipment_corporation(cr, version):
    cr.execute("""
        UPDATE ir_model_data
           SET module = '__export__'
         WHERE concat(module, '.', name) IN (
           'account.report_invoice_paid',
           'account.report_invoice_document_paid',
           'sale.report_invoice_layouted_paid',
           'sale_stock.report_invoice_document_inherit_sale_stock_paid'
         )
    """)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
        '39b15f26-b737-4420-94bb-156191526fbf': _boldom,
        'b23805af-ead8-4e0e-9254-c82a2845e971': _ngpinc,
        'a262570e-e3dd-42ba-bb91-064a02532221': _national_equipment_corporation,
    })
