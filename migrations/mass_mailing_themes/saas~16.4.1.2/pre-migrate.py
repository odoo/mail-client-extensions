from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("mass_mailing_themes.theme_{solar,promotion}_template"))
    util.rename_xmlid(cr, *eb("mass_mailing_themes.theme_{bold,magazine}_template"))
    util.rename_xmlid(cr, *eb("mass_mailing_themes.theme_{vip,coupon}_template"))
    util.rename_xmlid(cr, *eb("mass_mailing_themes.theme_{tech,blogging}_template"))
    util.rename_xmlid(cr, *eb("mass_mailing_themes.theme_{newsletter,event}_template"))
