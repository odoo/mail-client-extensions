# -*- coding: utf-8 -*-
# specific changes per db...
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    # some cleanup
    util.remove_module(cr, 'plugin')
    util.remove_module(cr, 'document_ftp')
    util.remove_module(cr, 'marketing_crm')

    util.new_module(cr, 'openerp_livechat', ('im_livechat', 'openerp_enterprise'))
    util.force_install_module(cr, 'openerp_livechat')
    rxids = util.splitlines("""
        assets_backend
        odoo_livechat_loader
    """)
    for x in rxids:
        util.rename_xmlid(cr, 'openerp_enterprise.' + x, 'openerp_livechat.' + x)

    fu = util.splitlines("""
        account.report_invoice_document
        crm.view_crm_case_leads_filter
        portal_sale.invoice_form_payment
    """)
    for x in fu:
        util.force_noupdate(cr, x, False)

    # this column is still a bpchar !?!
    cr.execute("ALTER TABLE stock_warehouse ALTER COLUMN code TYPE varchar")

    # partner_id is in fact an user_id (yuck!)
    # and the fk is not set (re-yuck!)
    # reset the wrong values
    util.fix_wrong_m2o(cr, 'website_crm_pageview', 'partner_id', 'res_users')

    # XXX move to a script for `openerp_enterprise` module?
    util.fix_wrong_m2o(cr, 'openerp_enterprise_database', 'admin_oauth_uid', 'res_users')

    # badly manually created xmlid: correct it
    cr.execute("UPDATE ir_model_data SET res_id=7453 WHERE id=1388307")

    # on 26/01/15, api create xml_id for custom fields with noupdate=true
    # delete them to avoid deletion of columns
    cr.execute("DELETE FROM ir_model_data WHERE create_uid=1599")

    # view without xmlid to update
    with util.skippable_cm(), util.edit_view(cr, view_id=7022) as arch:
        arch.attrib['expr'] = "//page[@name='geo_location']/group/group"

    # delete current `openerp.salesmen.invoices.odo` view. will be recreated when updating
    # `openerp_enterprise` module
    cr.execute("DELETE FROM ir_ui_view WHERE id=2261")

def migrate(cr, version):
    cr.execute("SELECT value FROM ir_config_parameter WHERE key=%s", ('database.uuid',))
    [uuid] = cr.fetchone()
    noop = lambda *a: None
    {
        '05a64ced-5b98-488d-a833-a994f9b1dd80': _db_openerp,    # test
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,    # prod
    }.get(uuid, noop)(cr, version)
