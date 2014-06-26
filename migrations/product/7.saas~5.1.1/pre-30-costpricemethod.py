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
    
    
    # Group costing method should be translated to group stock valuation costing method
    # This should only be done if it can find the valuation
    cr.execute("select res_id from ir_model_data WHERE module='stock' and name='group_inventory_valuation'")
    result = cr.fetchone()
    result = result and result[0] or False
    if result:
        cr.execute("select res_id from ir_model_data WHERE module='product' and name='group_costing_method'")
        result2 = cr.fetchone()
        result2 = result2[0] or False
        if result2:
            cr.execute("""select uid from res_groups_users_rel WHERE gid = %s""", (result,))
            not_ids = [x[0] for x in cr.fetchall()]
            if not_ids:
                cr.execute("""
                UPDATE res_groups_users_rel SET gid = %s WHERE gid = %s AND uid not in %s  
                """, (result, result2, tuple(not_ids),))
            else:
                cr.execute("""select * from res_groups_users_rel where gid = %s""", (result2, )) 
                res = cr.fetchall()
                cr.execute("""
                UPDATE res_groups_users_rel SET gid = %s WHERE gid = %s 
                """, (result, result2))