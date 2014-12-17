from os import environ as ENV


SAAS = ENV.get("OE_SAAS_MIGRATION")

def migrate(cr, version):
    if SAAS:
        # ensure saas_trial and its dependencies are (to) installed
        states = ('installed', 'to install', 'to upgrade')
        modules = tuple("saas_trial auth_oauth auth_signup web_analytics base_import".split())
        cr.execute("""UPDATE ir_module_module
                         SET state=%s
                       WHERE name IN %s
                         AND state NOT IN %s
                   """, ('to install', modules, states))
