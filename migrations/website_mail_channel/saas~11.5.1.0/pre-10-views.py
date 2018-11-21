# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "website_mail_channel.mail_channels", False)
    util.remove_record_if_unchanged(cr, "website_mail_channel.mail_template_list_subscribe")
    util.remove_record_if_unchanged(cr, "website_mail_channel.mail_template_list_unsubscribe")
