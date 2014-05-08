# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
from openerp.addons.base.maintenance.migrations import util
from openerp.osv import fields, osv
from openerp.tools.translate import _

def migrate(cr, version):
    # 1 Migrates all warehouses and create sequences and picking types and routes for them
    # 2 Attribute correct picking type to pickings
    registry = RegistryManager.get(cr.dbname)
    wh_obj = registry['stock.warehouse']
    location_obj = registry['stock.location']
    mod_obj = registry['ir.model.data']
    warehouses = wh_obj.search(cr, SUPERUSER_ID, [])
    main_warehouse = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.warehouse0')
    loc_whs = {}
    for wh in wh_obj.browse(cr, SUPERUSER_ID, warehouses):
        vals = {}
        lot_stock = wh.lot_stock_id
        lot_input = wh.lot_stock_id#wh.lot_input_id -> pre-migration?
        lot_output = wh.lot_stock_id #wh.lot_output_id -> pre-migration?
        if wh.id == main_warehouse:
            vals['code'] = 'WH'
        else:
            vals['code'] = wh.name[0:3].upper()

        # Make sure there is a separate view location for the warehouse.  If not, create one
        phys_loc = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.stock_location_locations')
        if lot_stock.location_id.id == phys_loc:
            # Create extra location as parent
            vals['view_location_id'] = location_obj.create(cr, SUPERUSER_ID, {'name':vals['code'], 'location_id': phys_loc})
            # Change
            location_obj.write(cr, SUPERUSER_ID, [lot_stock.id], {'location_id': vals['view_location_id']})
        else:
            vals['view_location_id'] = lot_stock.location_id.id
        
        loc_whs[vals['view_location_id']] = wh.id
        context = {'active_test': False}
        reception_steps = 'one_step'
        delivery_steps = 'ship_only'
        # If different and no chained => can not know this -> but we can do a pre!
        vals_loc = {}
        if lot_stock.id != lot_input.id:
            reception_steps = 'two_steps'
            vals['wh_input_stock_loc_id'] = lot_input.id
        else:
            #Create an inactive input location
            vals_loc['active'] = False
            vals['wh_input_stock_loc_id'] = location_obj.create(cr, SUPERUSER_ID, {'name': _('Input'), 
                                                               'active': False, 
                                                               'location_id': vals['view_location_id'],}, context=context)
        if lot_stock != lot_output:
            delivery_steps = 'pick_ship'
            vals['wh_output_stock_loc_id'] = lot_output.id
        else:
            vals['wh_output_stock_loc_id'] = location_obj.create(cr, SUPERUSER_ID, {'name': _('Output'), 
                                                                                    'active': False, 
                                                                                    'location_id': vals['view_location_id'],}, context=context)
        #Just need to create inactive Quality Control and inactive packing zone
        vals['wh_qc_stock_loc_id'] = location_obj.create(cr, SUPERUSER_ID, {'name': _('Quality Control'), 'active': False,
                                                                            'location_id': vals['view_location_id']}, context=context)
        vals['wh_pack_stock_loc_id'] = location_obj.create(cr, SUPERUSER_ID, {'name': _('Packing Zone'), 'active': False,
                                                                              'location_id': vals['view_location_id']}, context=context)
        
        
        wh_obj.write(cr, SUPERUSER_ID, [wh.id], vals) #Maybe do write directly through ORM instead of changing write code
        wh.refresh()
        wh_obj.create_sequences_and_picking_types(cr, SUPERUSER_ID, wh)
        
        #create routes and push/pull rules
        new_objects_dict = wh_obj.create_routes(cr, SUPERUSER_ID, wh.id, wh)
        wh_obj.write(cr, SUPERUSER_ID, wh.id, new_objects_dict)
        
        
    #Migrated pickings should be getting a picking type
    pick_obj = registry['stock.picking']
    picks = pick_obj.search(cr, SUPERUSER_ID, [])
    for pick in pick_obj.browse(cr, SUPERUSER_ID, picks):
        src_usage = pick.location_id.usage
        dest_usage = pick.location_dest_id.usage
        check_loc = (src_usage == 'internal') and pick.location_id or pick.location_dest_id
        parent_id = check_loc
        wh_locations = loc_whs.keys()
        result = False
        while parent_id:
            if parent_id.id in wh_locations:
                result = loc_whs[parent_id.id]
                break
            parent_id = parent_id.location_id
        if result: 
            warehouse = wh_obj.browse(cr, SUPERUSER_ID, result)
            pick_type = False
            if src_usage == 'internal' and dest_usage == 'internal':
                pick_type = warehouse.int_type_id.id
            elif src_usage == 'internal':
                pick_type = warehouse.out_type_id.id
            elif dest_usage == 'internal':
                pick_type = warehouse.in_type_id.id
            pick_obj.write(cr, SUPERUSER_ID, pick.id, {'picking_type_id': pick_type})