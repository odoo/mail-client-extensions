from openerp.addons.base.maintenance.migrations import util
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager

def migrate(cr, version):
    """
        Previous standard price should be set as first product price history at that time
    """
    
    cr.execute("""
    INSERT INTO product_price_history (cost, product_template_id, company_id, datetime)
    SELECT _standard_price_mig, id, company_id, NOW() FROM product_template WHERE company_id IS NOT NULL
    """)
    cr.execute("""
    INSERT INTO product_price_history (cost, product_template_id, company_id, datetime)
    SELECT _standard_price_mig, id, 1, NOW() FROM product_template WHERE company_id IS NULL
    """)
    
    
    # All packages with the same measurements should be grouped more or less?
    cr.execute("""
    INSERT INTO product_ul (name, length, width, height, weight, type)
    SELECT CONCAT('Pallet ', _length, 'x', _width, 'x', _height), _length, _width, _height, _weight_ul, 'pallet' FROM product_packaging 
    WHERE _length > 0 or _width > 0 or _height > 0 or _weight_ul > 0
    GROUP BY _length, _width, _height, _weight_ul
    """)
     
    cr.execute("""
    UPDATE product_packaging
    SET ul_container = pu.id
    FROM product_ul pu
    WHERE (_length > 0 or _width > 0 or _height > 0 or _weight_ul > 0) AND (_length = pu.length AND _width = pu.width 
    AND _height = pu.height AND _weight_ul = pu.weight)
    """)