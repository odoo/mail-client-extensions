from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'stock.product_category_form_view_inherit')
    cr.execute("update ir_model_data set module='stock_account' where name='stock_journal_sequence'")
    cr.execute("update ir_model_data set modeule='stock_account' where name='stock_journal'")
