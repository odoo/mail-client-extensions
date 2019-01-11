# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "website_mail_channel.mail_channels", False)
    util.if_unchanged(cr, "website_mail_channel.mail_template_list_subscribe", util.update_record_from_xml)
    util.if_unchanged(cr, "website_mail_channel.mail_template_list_unsubscribe", util.update_record_from_xml)
