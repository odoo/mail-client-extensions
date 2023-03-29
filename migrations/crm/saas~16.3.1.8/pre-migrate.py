# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_xmlid(cr, *eb("crm.action_{mark_as_lost,set_lost_with_reason}"))
    util.update_record_from_xml(cr, "crm.set_lost_with_reason")
