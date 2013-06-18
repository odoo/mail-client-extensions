from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.ensure_xmlid_match_record(cr, 'hr.ir_ui_view_sc_employee', 'ir.ui.view_sc', {
        'resource': 'ir.ui.menu',
        'res_id': util.ref(cr, 'hr.menu_open_view_employee_list_my'),
        'user_id': util.ref(cr, 'base.user_root'),
    })
