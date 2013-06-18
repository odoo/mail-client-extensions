from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.ref('portal_anonymous.anonymous_user'):
        util.remove_record(cr, 'portal_anonymous.anonymous_user_res_partner', deactivate=True)
