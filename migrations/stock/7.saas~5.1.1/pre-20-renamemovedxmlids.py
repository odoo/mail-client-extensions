from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        Move some record references from module, such that they are not recreated again
        Remove product category inherit form
    """
    util.remove_record(cr, 'stock.product_category_form_view_inherit')
    cr.execute("update ir_model_data set module='stock' where name='sequence_mrp_op_type'")
    cr.execute("update ir_model_data set module='stock_account' where name='stock_journal_sequence'")
    cr.execute("update ir_model_data set module='stock_account' where name='stock_journal'")
    