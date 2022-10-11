# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    script = util.import_script("mail/16.0.1.10/end-migrate.py")
    script.update_template_fs(cr, "sms.template")
