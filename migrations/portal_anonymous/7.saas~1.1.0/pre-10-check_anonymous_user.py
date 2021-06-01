from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.ensure_xmlid_match_record(cr, 'portal_anonymous.anonymous_user', 'res.users', {'login': 'anonymous'}):
        util.delete_unused(cr, 'portal_anonymous.anonymous_user_res_partner', deactivate=True)
