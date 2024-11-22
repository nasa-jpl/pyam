# Okay
"""SELECT repository FROM modulePackages
                     WHERE type='PACKAGE'
                     and name=%s
                     LIMIT 1
"""

# Bad
blah = "blah"
"""SELECT repository FROM modulePackages
                     WHERE type='PACKAGE'
                     and name='%s'
                     LIMIT 1
""" % blah
