from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
    Adapt sale order workflow to be entirely in sale module instead of sale_stock
    """
    cr.execute("update ir_model_data set module=%s where module=%s and model=%s", 
               ('sale', 'sale_stock', 'workflow.activity',))
    cr.execute("update ir_model_data set module=%s where module=%s and model=%s", 
               ('sale', 'sale_stock', 'workflow.transition',))

