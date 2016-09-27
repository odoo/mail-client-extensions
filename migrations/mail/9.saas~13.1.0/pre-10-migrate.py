# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, *util.expand_braces('{mass_mailing,mail}.icp_mail_bounce_alias'))
    util.force_noupdate(cr, 'mail.mail_template_data_notification_email_default', False)

    cr.execute('ALTER TABLE res_users ALTER COLUMN alias_id DROP NOT NULL')
    util.create_column(cr, 'mail_message_res_partner_needaction_rel', 'id', 'SERIAL')
