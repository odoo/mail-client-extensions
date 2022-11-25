# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    for pre, post in [
        ("page_unsubscribe", "page_mailing_unsubscribe"),
        ("page_unsubscribed", "page_mailing_unsubscribe_done"),
        ("unsubscribe", "unsubscribe_form"),
        ("unsubscribed", "unsubscribe_done"),
        ("view", "mailing_view"),
    ]:
        util.rename_xmlid(cr, f"mass_mailing.{pre}", f"mass_mailing.{post}")
