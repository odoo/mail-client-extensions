from odoo.upgrade import util


def migrate(cr, version):
    if util.parse_version(version) >= util.parse_version("saas~18.3"):
        util.remove_field(cr, "res.config.settings", "enabled_gmc_src")
        util.remove_field(cr, "res.config.settings", "gmc_xml_url")
        util.remove_constraint(cr, "website", "website_check_gmc_ecommerce_access")
