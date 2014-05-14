from openerp.addons.base.maintenance.migrations import util
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager

def migrate(cr, version):
    """
    Puts cost price and methods in properties where price is not 0 and cost method does not equal 'standard'
    It is doing this for company 1, but should do this for all companies?
    """
    registry = RegistryManager.get(cr.dbname)
    mod_obj = registry['ir.model.fields']
    fields_id = mod_obj.search(cr, SUPERUSER_ID, ['&', ('model', '=', 'product.template'), ('name', '=', 'standard_price')])[0]
    cr.execute("""
    INSERT INTO ir_property (create_uid, value_float, name, type, company_id, fields_id, res_id)
    SELECT 1, standard_price, 'standard_price','float', 1, %s, CONCAT('product.template,', product_template.id) FROM product_template WHERE standard_price <> 0.0
    """, (fields_id,))
    fields_id = mod_obj.search(cr, SUPERUSER_ID, ['&', ('model', '=', 'product.template'), ('name', '=', 'cost_method')])[0]
    cr.execute("""
    INSERT INTO ir_property (create_uid, value_text, name, type, company_id, fields_id, res_id)
    SELECT 1, cost_method, 'cost_method','selection', 1, %s, CONCAT('product.template,', product_template.id) FROM product_template WHERE cost_method <> 'standard'
    """, (fields_id,))
    util.rename_field(cr, 'product_template', 'standard_price', '_standard_price_mig')