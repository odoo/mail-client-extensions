# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    pv = util.parse_version

    util.rename_model(cr, "mail.test.full", "mail.test.ticket")
    util.rename_model(cr, "mail.test", "mail.test.container")
    util.rename_model(cr, "test_performance.mail", "mail.performance.thread")

    if pv(version) >= pv("saas~13.1"):
        util.rename_model(cr, "mail.test.tracking", "mail.performance.tracking")
    if pv(version) >= pv("saas~13.2"):
        util.rename_model(cr, "mail.test.compute", "mail.test.track.compute")

    util.rename_field(cr, "mail.test.ticket", "umbrella_id", "container_id")
    util.rename_field(cr, "mail.test.track", "umbrella_id", "container_id")

    renames = """
        st_mail_test_{full_umbrella,ticket_container}_upd
        st_mail_test{,_container}_default
        st_mail_test{,_container}_child_full

        mail_test_{full,ticket}_tracking_tpl
        mail_test{,_container}_tpl
        mail_test_{full,ticket}_tracking_view

        access_{test_performance_mail,mail_performance_thread}
        access_mail_{test,performance}_tracking_user
        access_mail_test_{full,ticket}_portal
        access_mail_test_{full,ticket}_user
        access_mail_test{,_container}_portal
        access_mail_test{,_container}_user
        access_mail_test{,_track}_compute
    """
    eb = util.expand_braces
    for rename in util.splitlines(renames):
        util.rename_xmlid(cr, *eb(f"mail_test.{rename}"))
