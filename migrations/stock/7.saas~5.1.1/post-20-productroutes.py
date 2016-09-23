# -*- coding: utf-8 -*-
import logging
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.stock.saas-5.'
_logger = logging.getLogger(NS + __name__)

def migrate(cr, version):
    """
        Link mto route with products that had route MTO
    """
    registry = RegistryManager.get(cr.dbname)
    mod_obj = registry['ir.model.data']
    mto_route = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.route_warehouse0_mto')
    cr.execute("""
    INSERT INTO stock_route_product (product_id, route_id)
    select id, %s from product_template where procure_method = 'make_to_order' 
    """, (mto_route,))


    if util.column_exists(cr, 'procurement_rule', '_product_id'): #When stock_location was installed
        # Let's create routes per product if there are pull/push related to this product
        # Might work more efficiently if we create an in between column on the route


        # Find procument rules with same products
        cr.execute("""
        SELECT _product_id, id, location_id, location_src_id, invoice_state, procure_method, action, company_id,
        partner_address_id, propagate, _picking_type FROM procurement_rule WHERE _product_id is not null
        ORDER BY location_id, location_src_id, invoice_state, procure_method, action, company_id, partner_address_id,
        propagate, _picking_type
        """)
        res = cr.fetchall()
        previous_line = []
        loc_obj = registry['stock.location']
        rule_prod_dict = {}
        for line in res:
            if line[2:] != previous_line:
                previous_line = line[2:]
                rule_prod_dict[line[2:]] = [line[0]]
            else:
                rule_prod_dict[previous_line] += [line[0]]

        product_obj = registry['product.template']
        product_var = registry['product.product']
        route_obj = registry['stock.location.route']
        pull_rule = registry['procurement.rule']
        for key, value in rule_prod_dict.items():
            # Put the rule in a separate route, for which you need the id to add to the corresponding products
            location = key[4] + ": " + (key[1] and loc_obj.browse(cr, SUPERUSER_ID, key[1]).name or '') + ' -> ' + loc_obj.browse(cr, SUPERUSER_ID, key[0]).name
            route_id = route_obj.create(cr, SUPERUSER_ID, {'name': location})
            
            # modules (mrp, purchase, ...) that extend this selection field are
            # not already installed when this script is run
            pull_rule._fields['action'].selection = [
                (item, item) for item in
                ('buy', 'manufacture', 'produce', 'move')]            

            key_betw = (route_id, location) + key
            pull_rule.create(cr, SUPERUSER_ID, {'name': location, 'route_id': route_id,
                                                        'location_id': key[0],
                                                        'location_src_id': key[1],
                                                        'invoice_state': key[2],
                                                        'procure_method': key[3],
                                                        'action': key[4],
                                                        'company_id': key[5],
                                                        'partner_address_id': key[6],
                                                        'propagate': key[7]})
            # Connect route with product templates
            templates = list(set(x.product_tmpl_id.id for x in product_var.browse(cr, SUPERUSER_ID, value)))
            product_obj.write(cr, SUPERUSER_ID, templates, {'route_ids': [(4, route_id)]})

        cr.execute("""
        DELETE FROM procurement_rule WHERE _product_id IS NOT NULL
        """)

        rules = pull_rule.search(cr, SUPERUSER_ID, [('picking_type_id', '=', False)])
        stock_move = registry['stock.move']
        type_obj = registry['stock.picking.type']
        for rule in pull_rule.browse(cr, SUPERUSER_ID, rules):
            if rule.action in ('produce','buy'):
                if rule.action in ('produce'):
                    rule.write({'action': 'manufacture'})
                types = [False]
            else:
                src_loc = rule.location_src_id
                dest_loc = rule.location_id
                code = stock_move.get_code_from_locs(cr, SUPERUSER_ID, False, src_loc, dest_loc)
                check_loc = src_loc if code == 'outgoing' else dest_loc
                wh = loc_obj.get_warehouse(cr, SUPERUSER_ID, check_loc)
                domain = [('code', '=', code)]
                if wh:
                    domain += [('warehouse_id', '=', wh)]
                types = type_obj.search(cr, SUPERUSER_ID, domain)
            if types and types[0]:
                pull_rule.write(cr, SUPERUSER_ID, [rule.id], {'picking_type_id': types[0]})


        #
        # DO THE SAME FOR PUSH RULES
        #

        # Find push rules with same products
        cr.execute("""
        SELECT _product_id, id, location_dest_id, location_from_id, invoice_state, company_id,
        propagate, delay, _picking_type FROM stock_location_path WHERE _product_id is not null
        ORDER BY location_dest_id, location_from_id, invoice_state, company_id,
        propagate, delay, _picking_type
        """)
        res = cr.fetchall()
        previous_line = []
        loc_obj = registry['stock.location']
        rule_prod_dict = {}
        for line in res:
            if line[2:] != previous_line:
                previous_line = line[2:]
                rule_prod_dict[line[2:]] = [line[0]]
            else:
                rule_prod_dict[previous_line] += [line[0]]

        push_rule = registry['stock.location.path']
        for key, value in rule_prod_dict.items():
            # Put the rule in a separate route, for which you need the id to add to the corresponding products
            location = (key[1] and loc_obj.browse(cr, SUPERUSER_ID, key[1]).name or '') + ' -> ' + loc_obj.browse(cr, SUPERUSER_ID, key[0]).name
            route_id = route_obj.create(cr, SUPERUSER_ID, {'name': location})

            key_betw = (route_id, location) + key
            push_rule.create(cr, SUPERUSER_ID, {'name': location, 'route_id': route_id,
                                                    'location_dest_id': key[0],
                                                    'location_from_id': key[1],
                                                    'invoice_state': key[2],
                                                    'company_id': key[3],
                                                    'propagate': key[4],
                                                    'delay': key[5]})

            # Connect route with product templates
            templates = [x.product_tmpl_id.id for x in product_var.browse(cr, SUPERUSER_ID, value)]
            product_obj.write(cr, SUPERUSER_ID, templates, {'route_ids': [(4, route_id)]})

        cr.execute("""
        DELETE FROM stock_location_path WHERE _product_id IS NOT NULL
        """)

        rules = push_rule.search(cr, SUPERUSER_ID, [('picking_type_id', '=', False)])
        stock_move = registry['stock.move']
        type_obj = registry['stock.picking.type']
        for rule in push_rule.browse(cr, SUPERUSER_ID, rules):
            src_loc = rule.location_from_id
            dest_loc = rule.location_dest_id
            code = stock_move.get_code_from_locs(cr, SUPERUSER_ID, False, src_loc, dest_loc)
            if code == 'outgoing':
                check_loc = src_loc
            else:
                check_loc = dest_loc
            wh = loc_obj.get_warehouse(cr, SUPERUSER_ID, check_loc)
            domain = [('code', '=', code)]
            if wh:
                domain += [('warehouse_id', '=', wh)]
            types = type_obj.search(cr, SUPERUSER_ID, domain)
            if types and types[0]:
                push_rule.write(cr, SUPERUSER_ID, [rule.id], {'picking_type_id': types[0]})


    # We need to move customer locations 'not under Customers' to 'under Customers'
    # This is needed as the procurement rule is in Customers
    location_obj = registry['stock.location']
    customer_loc = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.stock_location_customers')
    locations = location_obj.search(cr, SUPERUSER_ID, ['&', ('location_id.usage', '!=', 'customer'), '&', ('usage', '=', 'customer'), '!', ('id', 'child_of', customer_loc)])
    _logger.info("Linking location %s as parent of locations: %s",
                 customer_loc, ", ".join(map(str, locations)))
    location_obj.write(cr, SUPERUSER_ID, locations, {'location_id': customer_loc})
    util.remove_module(cr, 'stock_location')
