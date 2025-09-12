from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "sale_subscription"):
        query = """
            SELECT id
              FROM sale_order
             WHERE l10n_in_gst_treatment IS NULL
               AND is_subscription = True
            """
        util.recompute_fields(cr, "sale.order", ["l10n_in_gst_treatment"], query=query)
