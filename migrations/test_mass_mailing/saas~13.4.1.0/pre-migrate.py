# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "mass.mail.test", "mailing.test.blacklist")
    util.rename_model(cr, "mass.mail.test.bl", "mailing.performance.blacklist")
    util.rename_field(cr, "mailing.performance.blacklist", "umbrella_id", "container_id")

    renames = """
        access_{mass_mail_test,mailing_test_blacklist}_all
        access_{mass_mail_test,mailing_test_blacklist}_user
        access_{mass_mail_test_bl,mailing_performance_blacklist}_all
        access_{mass_mail_test_bl,mailing_performance_blacklist}_user
    """
    eb = util.expand_braces
    for rename in util.splitlines(renames):
        util.rename_xmlid(cr, *eb(f"mail_test.{rename}"))
