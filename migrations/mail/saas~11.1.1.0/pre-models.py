# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "mail_test"):
        # There is a circular reference between mail_test and mail_alias
        cr.execute("""ALTER TABLE mail_test DROP CONSTRAINT mail_test_alias_id_fkey""")

    util.remove_model(cr, "mail.test")
    for suffix in "simple track activity full".split():
        util.remove_model(cr, "mail.test." + suffix)
