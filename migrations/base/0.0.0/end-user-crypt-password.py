# -*- coding: utf-8 -*-
import os

from odoo import tools
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_gte("saas~11.4"):
        return

    if util.column_exists(cr, "res_users", "_upg_password_to_crypt"):
        util.remove_column(cr, "res_users", "password")
        cr.execute("ALTER TABLE res_users RENAME COLUMN _upg_password_to_crypt TO password")
        if not util.ref(cr, "__upgrade__.post_upgrade_encrypt_passwords"):
            cron_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "encrypt-password-cron.xml")
            with open(cron_file, "rb") as fp:
                tools.convert_xml_import(cr, "__upgrade__", fp, {})
    elif util.ref(cr, "__upgrade__.post_upgrade_encrypt_passwords"):
        util.remove_record(cr, "__upgrade__.post_upgrade_encrypt_passwords")
