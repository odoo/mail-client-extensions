from odoo.upgrade import util


def migrate(cr, version):
    # the keys fields are no longer necessary, the module uses an `auth_token`
    # with an Odoo proxy instead of directly contacting Amazon
    util.remove_field(cr, "amazon.account", "access_key")
    util.remove_field(cr, "amazon.account", "secret_key")

    # the NL marketplace is added in 13.5 in the data but may have been added
    # manually by users; since the api_ref field has a unique constraint, we must
    # ensure that the xmlid points to the correct record before the update tries
    # to create a duplicate record
    nl_mp = {
        "api_ref": "A1805IZSGTT6HS",
    }
    util.ensure_xmlid_match_record(cr, "sale_amazon.marketplace_NL", "amazon.marketplace", nl_mp)

    # the ir_config_param for the proxy URL needs to be renamed if it is present
    # force update from xmli
    util.update_record_from_xml(cr, "sale_amazon.proxy_url")
