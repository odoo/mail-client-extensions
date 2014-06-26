from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


def migrate(cr, version):
    
    registry = RegistryManager.get(cr.dbname)
    mod_obj = registry['ir.model.fields']
    # Create a new field already in stock_account and make properties based on the renamed old field valuation (_valuation_mig)
    # TODO: does work if stock_account is not to be installed?
    mo_obj = registry['ir.model']
    models = mo_obj.search(cr, SUPERUSER_ID, [('model', '=', 'product.template')])
    fields_id = mod_obj.create(cr, SUPERUSER_ID, {'model': 'product.template', 
                                                  'model_id': models[0], 
                                                  'name': 'valuation', 
                                                  'ttype': 'many2one', 
                                                  'state': 'base'})
    moddata_obj = registry['ir.model.data']
    moddata_obj.create(cr, SUPERUSER_ID, {'name': 'valuation', 'module': 'stock.account', 'res_id': fields_id, 'model': 'ir.model.fields'})
    
    cr.execute("""
    INSERT INTO ir_property (create_uid, value_text, name, type, company_id, fields_id, res_id)
    SELECT 1, _valuation_mig, 'valuation','selection', 1, %s, CONCAT('product.template,', product_product.product_tmpl_id) FROM product_product WHERE _valuation_mig <> 'manual_periodic'
    """, (fields_id,))
    fields_id = mod_obj.search(cr, SUPERUSER_ID, ['&', ('model', '=', 'product.template'), ('name', '=', 'cost_method')])[0]
    cr.execute("""
    INSERT INTO ir_property (create_uid, value_text, name, type, company_id, fields_id, res_id)
    SELECT 1, _cost_method, 'cost_method','selection', 1, %s, CONCAT('product.template,', product_template.id) FROM product_template WHERE _cost_method <> 'standard'
    """, (fields_id,))