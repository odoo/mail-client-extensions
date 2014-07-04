from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'res.partner', 'notification_email_send', 'notify_email')
    cr.execute("UPDATE res_partner SET notify_email=%s WHERE notify_email != %s", ('always', 'none'))
