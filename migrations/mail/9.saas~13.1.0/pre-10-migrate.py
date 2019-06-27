# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.version_gte("10.0") and util.ref(cr, "mail.icp_mail_bounce_alias"):
        # a duplicated xmlid has already be created by `mail/0.0.0/pre-icp.py`.
        cr.execute("DELETE FROM ir_model_data WHERE module = 'mass_mailing' AND name = 'icp_mail_bounce_alias'")
    else:
        util.rename_xmlid(cr, *util.expand_braces('{mass_mailing,mail}.icp_mail_bounce_alias'))

    util.force_noupdate(cr, 'mail.mail_template_data_notification_email_default', False)

    cr.execute('ALTER TABLE res_users ALTER COLUMN alias_id DROP NOT NULL')
    util.create_column(cr, 'mail_message_res_partner_needaction_rel', 'id', 'SERIAL PRIMARY KEY')

    # fix m2m
    cr.execute("ALTER TABLE mail_channel_res_group_rel RENAME COLUMN groups_id TO res_groups_id")
