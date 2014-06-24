from openerp.addons.base.maintenance.migrations import util
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager

def migrate(cr, version):
    """
    Puts cost price and methods in properties where price is not 0 / cost method does not equal 'standard'
    It is doing this only for company 1
    """
    registry = RegistryManager.get(cr.dbname)
    mod_obj = registry['ir.model.fields']
    fields_id = mod_obj.search(cr, SUPERUSER_ID, ['&', ('model', '=', 'product.template'), ('name', '=', 'standard_price')])[0]
    cr.execute("""
    INSERT INTO ir_property (create_uid, value_float, name, type, company_id, fields_id, res_id)
    SELECT 1, standard_price, 'standard_price','float', 1, %s, CONCAT('product.template,', product_template.id) FROM product_template WHERE standard_price <> 0.0
    """, (fields_id,))
    util.rename_field(cr, 'product.template', 'cost_method', '_cost_method')
    util.rename_field(cr, 'product.template', 'standard_price', '_standard_price_mig')