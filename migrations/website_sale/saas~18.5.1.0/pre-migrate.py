from odoo.upgrade import util


def migrate(cr, version):
    if util.parse_version(version) >= util.parse_version("saas~18.3"):
        util.remove_field(cr, "res.config.settings", "enabled_gmc_src")
        util.remove_field(cr, "res.config.settings", "gmc_xml_url")
        util.remove_constraint(cr, "website", "website_check_gmc_ecommerce_access")

        cr.execute("SELECT 1 FROM website WHERE enabled_gmc_src LIMIT 1")
        if cr.rowcount:
            # Pre-create the feature group and activate it if GMC was enabled on any website.
            util.update_record_from_xml(cr, "website_sale.group_product_feed")
            group_user_id = util.ref(cr, "base.group_user")
            group_product_feed_id = util.ref(cr, "website_sale.group_product_feed")
            cr.execute(
                """
                INSERT INTO res_groups_implied_rel (gid, hid)
                VALUES (%s, %s)
                """,
                [group_user_id, group_product_feed_id],
            )
            # Ensure all the website share the same configuration
            cr.execute("UPDATE website SET enabled_gmc_src = True")
