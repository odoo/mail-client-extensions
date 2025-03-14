from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
            SELECT 1
              FROM ir_property
             WHERE name='property_valuation'
               AND value_text='real_time'
             LIMIT 1
        """
    )
    if cr.rowcount:
        # feature is already being used => activate the "setting" for it
        usr_id = util.ref(cr, "base.group_user")
        xml_id = util.ref(cr, "stock_account.group_stock_accounting_automatic")
        util.env(cr)["res.groups"].browse(usr_id).write({"implied_ids": [(4, xml_id)]})
