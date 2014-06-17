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