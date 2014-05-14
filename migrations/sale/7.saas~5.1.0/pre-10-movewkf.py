from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("update ir_model_data set module=%s where module=%s and model=%s", 
               ('stock', 'sale_stock', 'workflow.activity',))
    cr.execute("update ir_model_data set module=%s where module=%s and model=%s", 
               ('stock', 'sale_stock', 'workflow.transition',))
    cr.execute("""DELETE from wkf_workitem w
                   USING wkf_instance i WHERE w.inst_id = i.id
                                          AND i.res_type=%s
               """, ('sale.order',))

