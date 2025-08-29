def migrate(cr, version):
    if version.startswith(("saas~18.2.", "saas~18.3.")):
        cr.execute("""
            UPDATE fleet_disallowed_expenses_rate
            SET rate = ABS(rate - 100.0);
        """)
