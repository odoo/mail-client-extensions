from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("18.0", "19.0") and util.module_installed(cr, "l10n_be"):
        cr.execute("SELECT id FROM res_company WHERE chart_template = 'be_comp' ORDER BY parent_path")
        for (company_id,) in cr.fetchall():
            orig_xmlid = "account.{}_virements_internes_template".format(company_id)
            orig_id = util.ref(cr, orig_xmlid)
            if not orig_id:
                continue
            new_xmlid = "account.{}_internal_transfer_reco".format(company_id)
            new_id = util.ref(cr, new_xmlid)
            util.rename_xmlid(cr, orig_xmlid, new_xmlid, on_collision="merge")
            if new_id:
                cr.execute("DELETE FROM account_reconcile_model WHERE id=%s", [new_id])
