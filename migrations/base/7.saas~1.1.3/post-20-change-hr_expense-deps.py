
def migrate(cr, version):
    # in march 2013, hr_expense got a new depend: account_accountant
    states = ('installed', 'to install', 'to upgrade')
    cr.execute("""UPDATE ir_module_module
                     SET state=%s
                   WHERE name=%s
                     AND state NOT IN %s
                     AND EXISTS(SELECT id
                                  FROM ir_module_module
                                 WHERE name=%s
                                   AND state IN %s
                                )
               """, ('to install', 'account_accountant', states, 'hr_expense', states))
