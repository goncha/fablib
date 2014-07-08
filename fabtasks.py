# -*- coding: utf-8 -*-

from fabric.api import run

def _generate_password():
    import string
    from random import sample
    chars = string.letters + string.digits
    return ''.join(sample(chars, 8))


def create_mysql_instance(mysql_user, mysql_password, instance_code):
    user = instance_code
    password = _generate_password()
    cmd_create_database = "/usr/bin/mysql -h localhost -u '%s' '--password=%s' -P %s -e \"create database %s;\"" % (
        mysql_user, mysql_password, 3306,
        user,)
    cmd_create_user = "/usr/bin/mysql -h localhost -u '%s' '--password=%s' -P %s -e \"grant all on %s.* to '%s'@'%%' identified by '%s';\"" % (
        mysql_user, mysql_password, 3306,
        user, user, password,)

    run(cmd_create_database)
    run(cmd_create_user)



# Local Variables: **
# comment-column: 56 **
# indent-tabs-mode: nil **
# python-indent: 4 **
# End: **
