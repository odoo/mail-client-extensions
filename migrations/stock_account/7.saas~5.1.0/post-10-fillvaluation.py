from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


def migrate(cr, version):
    
    registry = RegistryManager.get(cr.dbname)
    mod_obj = registry['ir.model.fields']
    #Search old field that will be updated -> is moved from product.product to product.template!
    fields_id = mod_obj.search(cr, SUPERUSER_ID, ['&', ('model', '=', 'product.template'), ('name', '=', 'valuation')])[0]
    cr.execute("""
    INSERT INTO ir_property (create_uid, value_text, name, type, company_id, fields_id, res_id)
    SELECT 1, _valuation_mig, 'valuation','selection', 1, %s, CONCAT('product.template,', product_product.product_template_id) FROM product_product WHERE _valuation_mig <> 'manual_periodic'
    """, (fields_id,))
    
    