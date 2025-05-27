from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("12.0") and util.column_exists(cr, "crm_team", "use_opportunities"):
        cr.execute("UPDATE crm_team SET use_opportunities=True WHERE use_opportunities IS NULL")
