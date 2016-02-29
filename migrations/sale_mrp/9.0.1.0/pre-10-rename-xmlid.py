# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
	util.rename_xmlid(cr, 'sale_mrp.view_mrp_production_form', 'sale_mrp.mrp_production_form_view_inherit_sale_mrp')

