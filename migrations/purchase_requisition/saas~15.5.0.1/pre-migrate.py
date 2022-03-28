# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "product.template", "purchase_requisition")
    util.remove_view(cr, "purchase_requisition.product_template_form_view_inherit")
    util.remove_record(cr, "purchase_requisition.tender_type_action")
    util.remove_menus(cr, [util.ref(cr, "purchase_requisition.menu_purchase_requisition_type")])
    util.remove_view(cr, "purchase_requisition.res_config_settings_view_form")
