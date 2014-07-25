# -*- coding: utf-8 -*-

from exceptions import RuntimeError

from fabric.api import run, cd



def _generate_password():
    import string
    from random import sample
    chars = string.letters + string.digits
    return ''.join(sample(chars, 8))

def _mysql_command(cmd):
    return "/usr/bin/mysql -h localhost -u '%s' '--password=%s' -P %s -e \"" + cmd + "\""


def delete_mysql_instance(mysql_user, mysql_password, instance_code, mysql_port):
    """Delete database and user on remote mysql instance."""
    if is_yigo_instance_running(instance_code):
        raise RuntimeError("Instance is running")

    user = instance_code
    database = instance_code
    # Clean already created instance
    cmd_drop_user = _mysql_command("drop user '%s'@'%%';") % (
        mysql_user, mysql_password, mysql_port,
        user,)
    cmd_drop_database = _mysql_command("drop database %s;") % (
        mysql_user, mysql_password, mysql_port,
        database,)
    run(cmd_drop_user, quiet=True);
    run(cmd_drop_database, quiet=True);


def delete_yigo_instance(instance_code):
    if is_yigo_instance_running(instance_code):
        raise RuntimeException("Instance is running")

    run("rm -rf apps/%s" % (instance_code,), quiet=True)


def create_mysql_instance(mysql_user, mysql_password, instance_code, mysql_port):
    """Create database and user on remote mysql instance.
    The value of `instance_code' are assigned to the name of database and user.
    The passwor of user are randomly generated.

    Returns
    -------
    (database_name, user, password) : tuple
       A tuple of database name, user, password.
    """
    # Delete existing mysql instance if exists
    delete_mysql_instance(mysql_user, mysql_password, instance_code, mysql_port)

    user = instance_code
    database = instance_code
    # Create new instance
    password = _generate_password()
    cmd_create_database = _mysql_command("create database %s;") % (
        mysql_user, mysql_password, mysql_port,
        database,)
    cmd_create_user = _mysql_command("create user '%s'@'%%' identified by '%s';") % (
        mysql_user, mysql_password, mysql_port,
        user, password,)
    cmd_grant = _mysql_command("grant all on %s.* to '%s'@'%%';") % (
        mysql_user, mysql_password, mysql_port,
        database, user,)
    run(cmd_create_database)
    run(cmd_create_user)
    run(cmd_grant)
    return database, user, password # Database name, username password


def create_yigo_instance(instance_code, configs_source, yigo_version="20140721"):
    """Create yigo instance directory layout, install yigo release pack and yigo app config pack.
    The process is completed successfully if no `Exception' raised."""
    # Clean existing yigo instance
    delete_yigo_instance(instance_code)

    # Create new instace
    configs_filename = configs_source.split('/')[-1]
    checksum_filename = configs_filename + '.sha256sum'
    checksum_source = configs_source + '.sha256sum'
    run("mkdir -p apps/%s/{cache,configs,data,logs,tmp,yigo}" % (instance_code,))
    run("tar -xf yigo-%s.tar.gz -C apps/%s/yigo" % (yigo_version, instance_code,))
    with cd('apps/%s/cache' % (instance_code,)):
        run("wget -q -O '%s' '%s'" % (checksum_filename, checksum_source,))
        run("wget -q -O '%s' '%s'" % (configs_filename, configs_source,))
        run("sha256sum -c '%s'" % (checksum_filename,))
        run("tar -xf '%s' -C '../configs'" % (configs_filename,))


def _get_pid_filename(instance_code):
    return 'apps/%s/tmp/pid' % (instance_code,)


def is_yigo_instance_running(instance_code):
    pid_filename = _get_pid_filename(instance_code)
    return run("test -e '%s' && ps -f -p $(<'%s') | grep 'yigo.instance=%s'" %
               (pid_filename, pid_filename, instance_code,), quiet=True).succeeded


def start_yigo_instance(instance_code, java_home, java_memory, db_host, db_port, db_name, db_user, db_password, port):
    if is_yigo_instance_running(instance_code):
        print "Instance is running"
        return
    else:
        # Find java command
        if java_home[-1] != '/':
            java_home = java_home + '/'
        java_exec = java_home + 'bin/java'
        # Process command arguments
        args = [java_exec, '-server']
        # Memory
        args.append('-Xms%sm' % (java_memory,))
        args.append('-Xmx%sm' % (java_memory,))
        args.append('-XX:MaxPermSize=128m')
        # Classpath
        args.append('-cp')
        args.append('"yigo/WEB-INF/classes:yigo/WEB-INF/lib/*:yigo/WEB-INF/lib/@deprecated/*:yigo/WEB-INF/lib/@deprecated/jetty/*"')
        # Yigo properties
        args.append('-Dserver.cloudregisterserver=http://1.1.8.16:8080/yigo')
        args.append('-Dserver.config=configs/main')
        args.append('-Dserver.generateYigoCss=false')
        args.append('-Dserver.dsn.description=default')
        args.append('-Dserver.dsn.default=Y')
        args.append('-Dserver.dsn.dbtype=3')
        args.append('-Dserver.dsn.name=default')
        args.append('-Dserver.db.default.conntype=jdbc')
        args.append('-Dserver.db.default.dbtype=3')
        args.append('-Dserver.db.default.driver=com.mysql.jdbc.Driver')
        args.append('\'-Dserver.db.default.url=jdbc:mysql://%s:%s/%s?useUnicode=true&amp;characterEncoding=UTF-8\'' %
                    (db_host, db_port, db_name,))
        args.append('-Dserver.db.default.user=%s' % (db_user,))
        args.append('-Dserver.db.default.pass=%s' % (db_password,))
        args.append('-DCODEBASE_SERVICE=yigo')
        args.append('-DAPP_SERVICE=yigo')
        args.append('-DAPP_SERVER=localhost:%s' % (port,))
        # Instance properties
        args.append('-Dyigo.home=yigo')
        args.append('-Dyigo.instance=%s' % (instance_code,))
        args.append('-Djava.io.tmpdir=tmp')
        # Main class
        args.append('test.start.StartHttpServer')
        # Arguments of main class
        args.append('yigo') # yigo install dir
        args.append('\'core@cloud\'') # empty core.properties

        cmd = ' '.join(args)
        with cd('apps/%s' % (instance_code,)):
            # Use `sleep 1` to wait the command starting up before fabric closes the ssh connection
            run('$(nohup ' + cmd + ' >& logs/nohup.out < /dev/null & echo $! > tmp/pid) && sleep 1')


def stop_yigo_instance(instance_code, force=False):
    signal = 'TERM'
    if force: signal = 'KILL'
    pid_filename = _get_pid_filename(instance_code)
    if is_yigo_instance_running(instance_code):
        run("kill -s %s $(<'%s') && rm '%s'" % (signal, pid_filename, pid_filename))



# Local Variables: **
# comment-column: 56 **
# indent-tabs-mode: nil **
# python-indent: 4 **
# End: **
