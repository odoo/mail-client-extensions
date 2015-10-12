# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE lunch_order SET state='new' WHERE state='partially'")

    util.create_column(cr, 'lunch_order', 'company_id', 'int4')
    cr.execute("""
        UPDATE lunch_order o
           SET company_id=u.company_id
          FROM res_users u
         WHERE u.id=o.user_id
    """)

    util.create_column(cr, 'lunch_order_line', 'category_id', 'int4')
    cr.execute("""
        UPDATE lunch_order_line l
           SET category_id=p.category_id
          FROM lunch_product p
         WHERE p.id=l.product_id
    """)

    util.delete_model(cr, 'lunch.cancel')
    util.delete_model(cr, 'lunch.order.order')
    util.delete_model(cr, 'lunch.validation')

    renames = {
        'lunch_order_line_search_view': 'lunch_order_line_view_search',
        'view_lunch_employee_payment_filter': 'lunch_cashmove_view_search',
        'view_lunch_cashmove_filter': 'lunch_cashmove_view_search_2',
        'view_search_my_order': 'lunch_order_view_search',
        'alert_search_view': 'lunch_alert_view_search',
        'casmove_tree_view': 'lunch_cashmove_view_tree',
        'casmove_form_view': 'lunch_cashmove_view_form',
        'action_lunch_order_form': 'lunch_order_action_form',
        'menu_lunch_order_form': 'lunch_order_menu_form',
        'action_lunch_order_tree': 'lunch_order_action_tree',
        'menu_lunch_order_tree': 'lunch_order_menu_tree',
        'casmove_tree': 'lunch_cashmove_view_tree_2',
        'action_lunch_cashmove_form': 'lunch_cashmove_action_account',
        'menu_lunch_cashmove_form': 'lunch_cashmove_menu_form',
        'action_lunch_order_by_supplier_form': 'lunch_order_line_action_by_supplier',
        'menu_lunch_order_by_supplier_form': 'lunch_order_line_menu_by_supplier',
        'action_lunch_control_suppliers': 'lunch_order_line_action_control_suppliers',
        'menu_lunch_control_suppliers': 'lunch_order_line_menu_control_suppliers',
        'action_lunch_control_accounts': 'lunch_cashmove_action_control_accounts',
        'menu_lunch_control_accounts': 'lunch_cashmove_menu_control_accounts',
        'action_lunch_cashmove': 'lunch_cashmove_action_payment',
        'menu_lunch_cashmove': 'lunch_cashmove_menu_payment',
        'action_lunch_product': 'lunch_product_action',
        'menu_lunch_product': 'lunch_product_menu',
        'action_lunch_product_categories': 'lunch_product_category_action',
        'product_category_form_view': 'lunch_product_category_view_form',
        'menu_lunch_product_categories': 'lunch_product_category_menu',
        'action_lunch_alert': 'lunch_alert_action',
        'menu_lunch_alert': 'lunch_alert_menu',
        'orders_order_line_tree_view': 'lunch_order_line_view_tree',
        'orders_tree_view': 'lunch_order_view_tree',
        'orders_form_view': 'lunch_order_view_form',
        'products_tree_view': 'lunch_product_view_tree',
        'products_form_view': 'lunch_product_view_form',
        'alert_tree_view': 'lunch_alert_view_tree',
        'alert_form_view': 'lunch_alert_view_form',
    }
    for o, n in renames.items():
        util.rename_xmlid(cr, 'lunch.' + o, 'lunch.' + n)
        util.force_noupdate(cr, 'lunch.' + n, False)
