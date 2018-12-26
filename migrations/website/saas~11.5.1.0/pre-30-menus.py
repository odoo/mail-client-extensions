# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # pre-11.5: top menu belongs to a website, but its children may not (if created in backend for example)
    # post-11.5: one menu hierarchy should belong to no website (template) and will be duplicated for new website
    # strategy: make hierarchy of website #1 the template, duplicate it for the main website and ensure all other
    #           hierarchies belong to their website correctly
    def recursive_menu_website(cr, menu_id):
        cr.execute("""
            WITH RECURSIVE submenus AS (
                SELECT id,website_id,parent_id
                FROM website_menu
                WHERE id = {}
                UNION
                SELECT m.id,m.website_id,m.parent_id
                FROM website_menu m
                INNER JOIN submenus s on s.id = m.parent_id)
            UPDATE website_menu wm SET website_id = submenus.website_id FROM submenus WHERE wm.id IN (SELECT id FROM submenus);
        """.format(menu_id))
    # step 1: find all top menus and apply the same website recursively on the hierarchy (useful for dbs with multiwebsite pre-11.5),
    #         except the menu of the first website will be made into a template in step 2
    cr.execute('SELECT id FROM website_menu WHERE parent_id IS NULL ORDER BY website_id ASC OFFSET 1')
    multi_top_menus = cr.dictfetchall()
    for top_menu in multi_top_menus:
        recursive_menu_website(cr, top_menu['id'])

    # step 2: take the menu hierarchy from the 1st website and make a template out of it
    #         by removing a link to a specific website
    cr.execute('SELECT id FROM website_menu WHERE parent_id IS NULL ORDER BY website_id ASC LIMIT 1')
    main_menu = cr.dictfetchone()
    cr.execute('UPDATE website_menu SET website_id=null where id={}'.format(main_menu['id']))
    recursive_menu_website(cr, main_menu['id'])
