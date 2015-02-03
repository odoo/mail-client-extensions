# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.new_module(cr, 'barcodes')
    util.new_module_dep(cr, 'barcodes', 'web')
    util.new_module_dep(cr, 'point_of_sale', 'barcodes')
    util.new_module_dep(cr, 'stock', 'barcodes')

    util.merge_module(cr, 'email_template', 'mail')

    util.new_module(cr, 'website_links')
    util.new_module_dep(cr, 'mass_mailing', 'website_links')

    util.new_module(cr, 'web_tip')
    util.new_module_dep(cr, 'web_tip', 'web')
    for m in 'account crm event hr project purchase website_quote'.split():
        util.new_module_dep(cr, m, 'web_tip')
