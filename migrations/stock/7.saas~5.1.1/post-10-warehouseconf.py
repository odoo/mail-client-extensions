# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
from openerp.addons.base.maintenance.migrations import util
from openerp.osv import fields, osv
from openerp.tools.translate import _

def migrate(cr, version):
    # 1 Migrates all warehouses and create sequences and picking types and routes for them
    # 2 Attribute correct picking type to pickings
    # 3 Create XML ids for the picking types in the main warehouse (for tests, ...)
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
        if wh.id == main_warehouse:
            vals['code'] = 'WH'
        else:
            vals['code'] = wh.name[0:3].upper()

        # Make sure there is a separate view location for the warehouse.  If not, create one
        phys_loc = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.stock_location_locations')
        if lot_stock.location_id.id == phys_loc:
            # Create extra location as parent
            vals['view_location_id'] = location_obj.create(cr, SUPERUSER_ID, {'name':vals['code'], 'location_id': phys_loc})
            location_obj.write(cr, SUPERUSER_ID, [lot_stock.id], {'location_id': vals['view_location_id']})
        else:
            vals['view_location_id'] = lot_stock.location_id.id
        
        loc_whs[vals['view_location_id']] = wh.id
        context = {'active_test': False}
        reception_steps = 'one_step'
        delivery_steps = 'ship_only'
        # If different and no chained => can not know this -> but we can do a pre!
        vals_loc = {}
        if wh.wh_input_stock_loc_id:
            reception_steps = 'two_steps'
            vals['wh_input_stock_loc_id'] = wh.wh_input_stock_loc_id.id
        else:
            #Create an inactive input location
            vals_loc['active'] = False
            vals['wh_input_stock_loc_id'] = location_obj.create(cr, SUPERUSER_ID, {'name': _('Input'), 
                                                               'active': False, 
                                                               'location_id': vals['view_location_id'],}, context=context)
        if wh.wh_output_stock_loc_id:
            delivery_steps = 'pick_ship'
            vals['wh_output_stock_loc_id'] = wh.wh_output_stock_loc_id.id
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
        wh.refresh()
        #create routes and push/pull rules
        new_objects_dict = wh_obj.create_routes(cr, SUPERUSER_ID, wh.id, wh)
        wh_obj.write(cr, SUPERUSER_ID, wh.id, new_objects_dict)
        
        
    #Migrated pickings should be getting a picking type
    pick_obj = registry['stock.picking']
    picks = pick_obj.search(cr, SUPERUSER_ID, [])
    
    main_wh = wh_obj.browse(cr, SUPERUSER_ID, main_warehouse)
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
            if src_usage == 'internal' and dest_usage != 'internal':
                pick_type = warehouse.out_type_id.id
            elif src_usage != 'internal' and dest_usage == 'internal':
                pick_type = warehouse.in_type_id.id
            else:
                pick_type = warehouse.int_type_id.id
        else:
            # Use internal of main warehouse
            pick_type = main_wh.int_type_id.id
        pick_obj.write(cr, SUPERUSER_ID, pick.id, {'picking_type_id': pick_type})
    
    
    #Create different XML ids (taken from yml files)
    partner_obj = registry['res.partner']
    mwhid = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.warehouse0')
    main_warehouse = wh_obj.browse(cr, SUPERUSER_ID, mwhid, context=context)
    mpid = mwhid = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'base.main_partner')
    partner_obj.write(cr, SUPERUSER_ID, mpid, {'property_stock_customer':main_warehouse.lot_stock_id.id})
    

    #create xml ids for demo data that are widely used in tests or in other codes, for more convenience
    xml_references = [
        {'name': 'stock_location_stock', 'module': 'stock', 'model': 'stock.location', 'res_id': main_warehouse.lot_stock_id.id},
        {'name': 'stock_location_company', 'module': 'stock', 'model': 'stock.location', 'res_id': main_warehouse.wh_input_stock_loc_id.id},
        {'name':'stock_location_output','module':'stock', 'model':'stock.location','res_id':main_warehouse.wh_output_stock_loc_id.id},
        {'name':'location_pack_zone','module':'stock', 'model':'stock.location','res_id':main_warehouse.wh_pack_stock_loc_id.id},
        {'name':'picking_type_internal','module':'stock', 'model':'stock.picking.type','res_id':main_warehouse.int_type_id.id},
        {'name':'picking_type_in','module':'stock', 'model':'stock.picking.type','res_id':main_warehouse.in_type_id.id},
        {'name':'picking_type_out','module':'stock', 'model':'stock.picking.type','res_id':main_warehouse.out_type_id.id},
    ]
    for xml_record in xml_references:
        xml_ids = mod_obj.search(cr, SUPERUSER_ID, [('module', '=', xml_record['module']), ('model', '=', xml_record['model']), ('name', '=', xml_record['name'])], context=context)
        if xml_ids:
            mod_obj.unlink(cr, SUPERUSER_ID, xml_ids) #Need to check this code further
        mod_obj.create(cr, SUPERUSER_ID, xml_record, context=context)
        #avoid the xml id and the associated resource being dropped by the orm by manually making a hit on it
        mod_obj._update_dummy(cr, SUPERUSER_ID, xml_record['model'], xml_record['module'], xml_record['name'])


