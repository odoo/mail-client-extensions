# -*- coding: utf-8 -*-
"""
    Fixup m2m tables that have been generated without FK by previous migration scripts.
    See https://github.com/odoo/saas-migration/commit/d072c67b89ab468f6da3cf858b987622d8522a2f
"""
import logging
from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.base.9.'
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    # cmr@saas-6
    util.fixup_m2m(cr, 'crm_lead_tag_rel', 'crm_lead', 'crm_lead_tag', 'lead_id', 'tag_id')
    util.fixup_m2m(cr, 'sale_order_tag_rel', 'sale_order', 'crm_lead_tag', 'order_id', 'tag_id')

    # ignore it, this table has not been migrated in 8.0 -> drop it (nobody complain, must not be very important)
    # fixup_m2m(cr, "im_session_im_user_rel", "im_session", "im_user")
    for tbl in "im_message_users im_session_im_user_rel im_message im_session im_user".split():
        cr.execute("DROP TABLE IF EXISTS " + tbl)

    # point_of_sale@saas-6
    util.fixup_m2m(cr, 'account_tax_pos_order_line_rel', 'pos_order_line', 'account_tax')

    # producte@saas-5
    util.fixup_m2m(cr, 'product_attribute_value_product_product_rel',
              'product_attribute_value', 'product_product', 'att_id', 'prod_id')
    util.fixup_m2m(cr, 'product_attribute_line_product_attribute_value_rel',
              'product_attribute_line', 'product_attribute_value', 'line_id', 'val_id')

    # purchase_requistion@saas-6
    util.fixup_m2m(cr, 'purchase_requisition_supplier_rel',
              'purchase_requisition_partner', 'res_partner', 'requisition_id', 'partner_id')

    # website_sale@saas-5
    if util.module_installed(cr, "website_sale"):
        util.fixup_m2m(
            cr, "product_public_category_product_template_rel", "product_template", "product_public_category"
        )
    else:
        cr.execute(
            """
            DROP TABLE IF EXISTS product_public_category_product_template_rel;
            DROP TABLE IF EXISTS product_style_product_template_rel;
            DROP TABLE IF EXISTS product_alternative_rel;
            DROP TABLE IF EXISTS product_accessory_rel;
        """
        )
