from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website.s_quotes_carousel", util.update_record_from_xml, reset_translations={"arch_db"})
