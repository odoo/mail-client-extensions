# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    rt = dict(reset_translations={"subject", "body_html"})

    util.if_unchanged(cr, "helpdesk.new_ticket_request_email_template", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "helpdesk.solved_ticket_request_email_template", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "helpdesk.rating_ticket_request_email_template", util.update_record_from_xml, **rt)

    util.if_unchanged(
        cr, "helpdesk.digest_tip_helpdesk_0", util.update_record_from_xml, reset_translations={"tip_description"}
    )
