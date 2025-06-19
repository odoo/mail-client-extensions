def migrate(cr, version):
    if not version.startswith(("saas~18.2.", "saas~18.3.")):
        return
    cr.execute("""
        UPDATE fleet_disallowed_expenses_rate
        SET rate = ABS(rate - 100.0);
    """)
