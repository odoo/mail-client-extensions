def migrate(cr, version):
    # Disallowed rate field becomes Deductible rate
    cr.execute("UPDATE fleet_disallowed_expenses_rate SET rate = 100.0 - rate")
