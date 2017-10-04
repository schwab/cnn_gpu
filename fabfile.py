import os
from fabric.api import *
from fabric.contrib.files import exists
from getpass import getpass
import logging
from StringIO import StringIO

code_dir = "/mnt/extradrive1/projects/pyimagesearch"

repo_url = "git@bitbucket.org:mdmetrix/qiadvisor.deploy.git"
required_app_dirs = []
dirs = {"deploy":code_dir
   }
sudo_user = "la-mschw6"
pull_services = []
build_services = []
pwd = None
all_service_names = []
service_names = []
api_test_files = [
    
    ]
api_newman_tests = [""]
# State
env_dict = {
    "prod":{"sub_domain":"net","use_saml":"true", "scheme":"https"}, 
    "staging":{"sub_domain":"org", "use_saml":"false", "scheme":"https"}, 
    "dev":{"sub_domain":"dev", "use_saml":"false", "scheme":"http"}}
env.verbose = False

def log():
    logging.basicConfig(level=logging.DEBUG)  

@task
def prod(user=None):
    """Set the fab state to the production server. All subsequent calls will be against prod. Provide admin user name (ie fab staging:admin_user pull)."""
    if user is None:
        #print "No user name specified (fab prod:<username>)"
        raise Exception("User name is required (fab prod:<username>)")
    env.user = user
    #env.hosts = "www.qiadvisor.%s" % (env_dict["prod"]["sub_domain"])
    env.name = "prod"  

@task
def staging(user=None):
    """Set the fab state to the staging server. All subsequent calls will be against staging. Provide admin user name (ie fab prod:admin_user pull))"""
    if user is None:
        #print "No user name specified (fab prod:<username>)"
        raise Exception("User name is required (fab staging:<username>)")
    env.user = user
    env.hosts = "www.qiadvisor.%s" % (env_dict["staging"]["sub_domain"])
    env.name = "staging"

@task
def dev(user=None):
    env.name="dev"
    #env.hosts = "www.qiadvisor.%s" % (env_dict["dev"]["sub_domain"])
    env.user = ""

@task
def verbose():
    env.verbose=True

# Actions
def split_comma(names=""):
    return names.split(',')

def arg_bool_eval(arg):
    if type(arg) is bool:
        return arg
    elif arg is not None and arg.lower() in ('yes', 'true', 't', 'y', '1', 'hammer-time'):
        return True
    else:
        return False

@task
def allow_access():
    if "dev" in env.name:
        for dir in required_app_dirs:
            local("sudo chmod 777 %s" % (dir))
@task
def bash(command):
    """Run an arbitrary bash command on the host in the deploy direcotry (ie fab staging bash:command='ls -la /mnt')
    """
    with cd(dirs["deploy"]):
        run("%s" % (command))
@task
def backup_code():
    """Backup the code in /mnt/resource/qiadvisor.deploy to /mnt/resource/qiadvisor.deploy.tar"""
    backup_file_name = "/mnt/resource/qiadvisor.deploy.tar"
    commands =[]
    if "dev" in env.name:
        if os.path.isdir(backup_file_name):
            commands.append("rm %s" % (backup_file_name))
    else:
        if exists(backup_file_name):
            commands.append("rm %s" % (backup_file_name))
    
    #commands.append("cd /mnt/resource")
    commands.append("tar -zcvf %s /mnt/resource/qiadvisor.deploy" % (backup_file_name))
    sudo_commands(commands)

@task(alias="ccode")
def clean_code(branch="staging"):
    """Start with a fresh code direcory :  rm -rf /mnt/resource/qiadvisor_deploy then git clone the deploy repo."""
    if "dev" in env.name :
        if not os.path.isdir(dirs["parent"]):
            print 'The path %s must exist before pulling code.' % (dirs["parent"])
        if os.path.isdir(dirs["deploy"]):
            local("sudo rm -rf %s" % (dirs["deploy"]))
        os.chdir(dirs["parent"])
        local("sudo chmod 777 %s" % (dirs["parent"]))
        #local("sudo ls -la ~/")
        local("git clone %s" % (repo_url))
        os.chdir(dirs["deploy"])
        local("git submodule init")
        local("git submodule update")
    else:
        sudo("rm -rf %s" % (dirs["deploy"]))
        with cd(dirs["parent"]):
            sudo("git clone %s" % (repo_url))
        with cd(dirs["deploy"]):
            sudo("git submodule init")
            sudo("git submodule update")

@task(alias="cdock")
def clean_docker():
    """Clean dngling images and prune. This safely removes unused images and containers. """
    steps = [
        "docker system df", 
        "docker images --quiet --filter=dangling=true | xargs --no-run-if-empty docker rmi -f",
        "docker system prune",
        "docker system df"
        ]
    if "dev" in env.name:
        for s in steps:
            local(s)
    else:
        for s in steps:
            run(s)

@task(alias="cdf")
def create_data_folders():
    """Create data folders and other required application volume paths. Automatically called by install."""
    for path in required_app_dirs:
        if "dev" in env.name:
            if not os.path.isdir(path):
                local("sudo mkdir %s" % (path))
        else:
            if not exists(path, use_sudo=True):
                sudo("mkdir %s" % (path))

@task(alias="dc")
def docker_compose(command):
    """Run arbitrary docker-compose commands (ie fab staging dc:'up')"""
    commands = ["docker-compose %s" %(command)]
    run_commands(commands)

@task(alias="di")
def docker_info():
    """Get docker host information"""
    commands = ["docker info"]
    run_commands(commands)

@task(aliases=["dp","publish"])
def deploy(branch="staging", clean_data=False, parallel=False):
    """Deploy the specified branch (pull, image_pull, image_build,down and up)
    """
    clean_data = arg_bool_eval(clean_data)
    parallel = arg_bool_eval(parallel)
    
    pull(branch)
    image_pull(parallel)
    image_build()
    down()
    up(detached=True)
    copy_sourcedata()
    import_data(clean_data)
    logs(follow="true")

@task
def df():
    """Run df on host (ie fab staging df)"""
    commands = ["df"]
    run_commands(commands)

@task(alias="ps")
def docker_ps():
    """Show all running docker containers"""
    commands = ["docker ps"]
    run_commands(commands)

@task
def down(flags=None):
    """ Run docker-compose down on the server specified (ie fab staging down)
    """
    if "dev" in env.name:
        commands = ["docker-compose -f docker-compose.yml -f docker-compose-dev.yml down --remove-orphans"]
    else:
        commands = ["docker-compose down --remove-orphans"]
    run_commands(commands, warn_only=True)

@task
def git(command):
    """Run the provided command using git
    (ie fab staging git:status or fab staging git:'pull origin master')"""
    commands = ["git %s" % (command)]
    run_commands(commands)

@task
def install(branch="staging"):
    """Perform git clone the repo into the
    /mnt/resource directory and run the deploy steps."""
     # setup virtual mem setting required for elk
    if "dev" not in env.name:
       PASS
    create_data_folders()
    clean_code(branch)
    deploy(branch, clean_data=True)

@task(aliases=["ib","build"])
def image_build(service=None):
    """Perform a docker-compose build on each of the services.
    """
    if not service is None:
        if service in build_services:
            if "dev" in env.name:
                os.chdir(dirs["deploy"])
                local("docker-compose  -f docker-compose.yml -f docker-compose-dev.yml build %s" % (service))
            else:
                with cd(dirs["deploy"]):
                    run("docker-compose build %s" % (service))
        else:
            print "%s is not a service which can be built must be one of : %s" \
                % (service, build_services)
    else:
        for service in build_services:
            if "dev" in env.name:
                with settings(warn_only=True):
                    os.chdir(dirs["deploy"])
                    local("docker-compose -f docker-compose.yml -f docker-compose-dev.yml  build %s" % (service))
            else:
                with settings(warn_only=True):
                    with cd(dirs["deploy"]):
                        run("docker-compose build %s" % (service))
@task
def image_pull(parallel=False):
    """Pull the images for the services specified in the docker-compose.yml file.
    """
    p_string = "--parallel" if arg_bool_eval(parallel) else ""
    pull_images = ' '.join(map(str, pull_services))
    if "dev" in env.name:
        os.chdir(dirs["deploy"])
        with settings(warn_only=True):
            local("docker-compose -f docker-compose.yml -f docker-compose-dev.yml pull %s %s" % (p_string, pull_images))
    else:
        with cd(dirs["deploy"]):
            with settings(warn_only=True):
                run("docker-compose pull %s %s " % (p_string, pull_images))

def list_services():
    fh = StringIO()
    if "dev" in env.name:
        os.chdir(dirs["deploy"])
        result = local("docker-compose -f docker-compose.yml -f docker-compose-dev.yml config --services", capture=True)
        lines = result.split("\n")
        return lines
    else:
        with cd(dirs["deploy"]):
            run("docker-compose config --services", stdout=fh)
    fh.seek(0)
    lines = fh.readlines()
    print "%s" % (lines[0].split(":")[0])
    services_list =  [l.split(":")[1].rstrip().lstrip() for l in lines][:-1]
    return services_list

@task
def logs(service=None, follow=False):
    f = "-f" if arg_bool_eval(follow) else ""
    commands = []
    if service is None:
        commands.append("docker-compose logs %s" % (f))
    else:
        commands.append("docker-compose logs %s %s" % (f, service))
    run_commands(commands)

@task(alias='p')
def pull(branch="staging"):
    """Pull the latest code and update all submodules.
    """
    commands =[
            "git reset --hard HEAD~0", 
            "git clean -fd",
            "git submodule foreach git reset --hard", 
            "git submodule foreach git clean -fd", 
            "git checkout %s" %(branch), 
            "git reset --hard HEAD~0", 
            "git clean -fd",
            "git submodule foreach git reset --hard", 
            "git submodule foreach git clean -fd", 
            "git pull origin %s" % (branch), 
            "git submodule update --init"]
    if "dev" in env.name:
        run_commands(commands)
    else:        
        sudo_commands(commands)
    #sudo("git status")
    login = not "dev" in env.name
    sed_webservice(enforce_login=login)
    sed_ui()
    sed_dc()
    sed_saml()
    copy_sourcedata()

@task(alias='purge')
def purge_images(like=None):
    if like is None:
        commands = ["docker-compose rm -f", "docker rm $(docker ps -a -q)", "docker rmi $(docker images -q)"]
    else:
        commands = ["docker ps -a | grep '%s' | awk '{print $1}' | xargs docker rm -f" % (like)]
    run_commands(commands, warn_only=True)

@task(alias="r")
def restart(names=""):
    """ docker-compose restart. Use comma seperated service names to specify a list of services.
    """
    services = split_comma(names)
    commands = []
    for service in services:
        commands.append("docker-compose restart %s" % (service))
    run_commands(commands)    

def run_commands(commands, warn_only=False, run_dir=dirs["deploy"]):
    """
    Run one or more commands based on the current env.name (dev is local, otherwise remote)
    """
    warn_only = arg_bool_eval(warn_only)
    if "dev" in env.name:
        os.chdir(run_dir)
        for c in commands:
            if warn_only:
                with settings(warn_only=True):
                    local(c)
            else:
                local(c)
    else:
        with cd(run_dir):
            for c in commands:
                if warn_only:
                    with settings(warn_only=True):
                        run(c)
                else:
                    run(c)   
        
    
@task(alias="ls")
def services():
    """List all docker-compose services."""
    ls = list_services()
    for item in ls:
        print item

@task(alias="s")
def stats():
    """Run docker stats to show running container and their resource usage"""
    run_commands(["docker stats $(docker ps --format={{.Names}})"])

@task
def stop(service):
    """
    Stop the service specified
    """
    if "dev" in env.name:
        commands = ["docker-compose -f docker-compose.yml -f docker-compose-dev.yml stop %s " % (service)]
    else:
        commands = ["docker-compose stop %s" % (service)]
    run_commands(commands)

def su(pwd, user, command):
    with settings(
        password= "%s" % pwd,
        sudo_prefix="su %s -c " % user,
        sudo_prompt="Password:"
        ):
        sudo(command)

@task
def sudo_command(command):
    """ Run a command with sudo in the deploy directory."""
    sudo_commands([command])

def sudo_commands(commands, warn_only=False, run_dir=dirs["deploy"]):
    warn_only = arg_bool_eval(warn_only)
    if "dev" in env.name:
        sudo_commands = ["sudo %s" % (x) for x in commands]
        run_commands(sudo_commands, warn_only, run_dir)
    else:
         with cd(run_dir):
            for c in commands:
                if warn_only:
                    with settings(warn_only=True):
                        sudo(c)
                else:
                    sudo(c)   

@task
def test(api_path="./source/qiadvisor.api.cohort/WebService",like=None, list=False):
    if list:
        for line in api_test_files:
            print line
    else:    
        if "dev" in env.name:
            os.chdir(api_path)
            for f in api_test_files:
                if (not like is None and like in f) or like is None:
                    local("python -m unittest %s" % ( f))

@task
def term(service=None):
    """Create an interactive terminal on the host (ie fab staging term). If a service name is provided, then terminal to it instead.
    """
    if not service is None:
        ls = list_services()
        if not service in ls:
            print 'Service name should be one of these (instead of [%s]) :' % (service)
            for s in ls:
                print "\t%s" % (s)
            return
    if "dev" in env.name:
        print "Interactive terminal does not work on local host. Try one of these commands instead..."
        print "docker-compose exec %s sh" % (service)
        print "docker-compose exec %s bash" % (service)
        return
    #with cd("%s" % (dirs["deploy"])):
    if service is None:
        open_shell()
    else:
        open_shell("cd %s && docker-compose exec %s sh" % (dirs["deploy"], service))

@task
def up(servers=None, detached=False):
    """Bring up the docker services specified (comma separated) or all of them if no servers specified. """
    commands = []
    d = "-d" if arg_bool_eval(detached) else ""
    if not servers is None:
        slist = servers.split(';')
        for s in slist:
            commands.append("docker-compose up %s %s" % (s, d))
    else:       
        if "dev" in env.name:
            commands.append("docker-compose -f docker-compose.yml -f docker-compose-dev.yml up %s" % (d))
        else:
            commands.append("docker-compose up")
    run_commands(commands, warn_only=True)
    
