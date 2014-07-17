# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_template', 'track_incoming', 'boolean')
    util.create_column(cr, 'product_template', 'track_outgoing', 'boolean')
    cr.execute("""
        UPDATE product_template SET track_incoming = pp.track_incoming, track_outgoing = pp.track_outgoing
        FROM product_product pp WHERE product_template.id = pp.product_tmpl_id 
    """)
    
    cr.execute("""
        UPDATE stock_move SET priority = '2' 
        WHERE priority = '1'
    """)
    
    
    #Valuation and product template
    cr.execute("update ir_model_fields set model='product.template' where model='product.product' and name='valuation' returning id")
    res = cr.fetchall()
    cr.execute("""update ir_property ip set res_id = CONCAT('product.template,',p.product_tmpl_id) 
                from product_product p where ip.res_id=CONCAT('product.product', p.id) and ip.fields_id = %s and ip.name='valuation'""", (res[0][0],)) #p.id=split_part(ip.res_id,',',2)::int
    
    #cr.execute("delete from ir_model_data where name='field_product_product_valuation' and model='ir.model.fields'")