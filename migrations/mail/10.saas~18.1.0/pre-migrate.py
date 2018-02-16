# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'mail.followers', 'res_model_id')

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('mail.mail_smiley_{,normal_}smile'))
    util.rename_xmlid(cr, *eb('mail.mail_smiley_{laugh,smile}'))
