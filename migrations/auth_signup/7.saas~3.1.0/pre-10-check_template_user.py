from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    xid = 'auth_signup.default_template_user'
    if not util.ensure_xmlid_match_record(cr, xid, 'res.users', {'login': 'portaltemplate'}):
        util.delete_unused(cr, xid + '_res_partner', deactivate=True)
