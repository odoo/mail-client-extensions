from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("16.0", "17.0") and not util.ref(cr, "loyalty.config_online_sync_proxy_mode"):
        util.update_record_from_xml(cr, "loyalty.config_online_sync_proxy_mode")
        util.add_to_migration_reports(
            """
            The system parameter {} was set to <code>False</code>.
            This improves performance while opening or creating a record in 'Gift cards & e-wallet'
            menu, especially when there are many products.
            If you experience any issue you could try setting it to <code>True</code>.
            """.format(
                util.get_anchor_link_to_record(
                    "ir.config_parameter",
                    util.ref(cr, "loyalty.config_online_sync_proxy_mode"),
                    "loyalty.compute_all_discount_product_ids",
                )
            ),
            category="Loyalty",
            format="html",
        )
