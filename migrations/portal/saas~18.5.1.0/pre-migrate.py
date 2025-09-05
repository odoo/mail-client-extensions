from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("portal.address_{row,list}"))
    util.rename_xmlid(cr, *eb("portal.address_{kanban,card}"))
