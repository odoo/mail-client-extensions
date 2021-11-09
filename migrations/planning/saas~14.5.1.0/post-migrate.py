# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rt = dict(reset_translations={"subject", "body_html"})

    util.if_unchanged(cr, "planning.email_template_slot_single", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "planning.email_template_planning_planning", util.update_record_from_xml, **rt)
