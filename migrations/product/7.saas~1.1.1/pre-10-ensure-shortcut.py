from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.ensure_xmlid_match_record(cr, 'product.ir_ui_view_sc_product0', 'ir.ui.view_sc', {
        'resource': 'ir.ui.menu',
        'res_id': util.ref(cr, 'product.menu_products'),
        'user_id': util.ref(cr, 'base.user_root'),
    })
