def migrate(cr, version):
    cr.execute("ALTER TABLE employee_category_rel RENAME COLUMN emp_id TO employee_id")
