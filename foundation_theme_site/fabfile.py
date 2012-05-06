from fabric.api import *
from fabric.contrib.files import *
import yaml
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from fabric.contrib import django
from datetime import date
import os
import sys

from os.path import abspath, dirname, join,split
from site import addsitedir
PROJECT_PATH=split(os.path.abspath(os.path.dirname(__file__)))[1]



@task
def production():
    CFG=yaml.load(open('_deploy.cfg'))
    env.hosts=CFG['hosts']
    env.sites=CFG['sites']
    env.project=PROJECT_PATH
    env.virtualenvs=CFG['virtualenvs']
    env.directory = join(env.sites,'foundation-design-patterns',PROJECT_PATH)
    env.python=join(env.virtualenvs,"%s-env/bin/python" % PROJECT_PATH)
    env.nginx_root=CFG['nginx_root']
    env.gunicorn= CFG['gunicorn']
    env.user = CFG['user']
    env.memcache=CFG['memcache']
    env.db_user=CFG["db_user"]                  
    env.db_passwd=CFG["db_passwd"]
    env.db_host = CFG["db_host"] 
    env.db_name= CFG["db_name"] 
    
@task
def create_virtualenv():
    """
    Create the virtualenv for the project
    """
    with settings(warn_only=True):
        if run("test -d %s%s-env" % (env.virtualenvs,env.project)).failed:
            run('mkvirtualenv %s-env' % env.project)
            
@task   
def clone_project():
    """
    Clone the deployment user's fork of the upstream master
    """
    with settings(warn_only=True):
        with cd(env.sites):
            if run("test -d %s" % env.directory).failed:
                run('git clone git://github.com/chrisdevdeploy/foundation-design-patterns.git')
        
@task   
def add_upstream(): 
    """
    Add the remote upstream
    """
    with settings(warn_only=True):
        with cd(join(env.sites,'foundation-design-patterns')):
             run('git remote add upstream git://github.com/chrisdev/foundation-design-patterns.git')
             
@task
def enable_site():
    """
    Create the symbolic link in the nginx sites-enabled directory to the
    nginx config for the site
    """
    with cd('/etc/nginx/sites-enabled/'):
        with settings(warn_only=True):
            sudo('ln -s /etc/nginx/sites-available/%s %s' % (env.project,env.project))
    sudo('/etc/init.d/nginx configtest')
    
@task        
def bootstrap():
    """Everything need to get project running on this server"""
    create_virtualenv()
    clone_project()
    update_requirements()
    deploy_conf_files()
    migrate_syncdb()
    with settings(warn_only=True):
        with cd(env.directory):
            run('mkdir logs')
    #sudo supervisorctl reread
    #sudo supervisorctl add foundation_theme_site
@task    
def virtualenv(command):
    """
    Enable the virtualenv
    """
    with cd(env.directory):
        
        run('source %s%s-env/bin/activate && %s' % (env.virtualenvs,env.project,command))
        

@task       
def update_repo():
    """
    Update from master - We have a deployment user account with a fork of the master
    """
    with cd(env.directory):
        run('git pull upstream master')
           
@task
def update_requirements():
    """
    Install new requirements if any
    """
    virtualenv('pip install -r requirements/project.txt')  
     
@task    
def migrate():
    """
    Run the south  migrate.
    """
    
    with cd(env.directory):
       with settings(warn_only=True):
           run(env.python + " manage.py migrate --all")    
        
@task   
def syncdb():
    """
    Run the syncdb 
    """
    with cd(env.directory):
        run(env.python + " manage.py syncdb")

@task
def migrate_syncdb():
    migrate()
    syncdb()
    
@task       
def build_static():
    """
    Copy the static files (images,css,js) to site_media 
    """
    with cd(env.directory):
        run(env.python + " manage.py  collectstatic --noinput")

@task
def nginx_reload():
    """
    Reload the nginx server 
    """
    sudo("/etc/init.d/nginx reload")
@task    
def gunicorn_reload():
    with settings(warn_only=True):
        sudo("sudo supervisorctl restart %s" % PROJECT_PATH)
        


@task   
def maint_mode():
    """
    Put the site in maintenence mode
    """
    with settings(warn_only=True):
        with cd('%s/site_media/static' % env.directory):
            run('touch maint.html')
        
@task       
def production_mode():
    """
    Puts the site into production mode
    """
    gunicorn_reload()
    with cd('%s/site_media/static' % env.directory):
        run('rm maint.html')
@task   
def deploy_local_settings():
    """
    Upload and configure the local_settings template 
    Store dbuser etc. in _deploy.cfg
    """
    destination= join(env.directory,"local_settings.py") 
    
    upload_template('deploy/local_settings_tmpl.py',destination,context=env)
           
@task       
def deploy_nginx():
    """
    Upload and configure the  nginx template 
    Store the nginx settings in _deploy.cfg
    """
    upload_template('deploy/nginx.conf', join(env.nginx_root,env.project),context=env,use_sudo=True)  
@task        
def deploy_supervisor():
    """
    Upload and configure the supervisord template 
    Store the ngix settings in _deploy.cfg
    """
    destination="/etc/supervisor/conf.d/%s.conf" % env.project
    upload_template('deploy/supervisor.conf',destination, context=env,use_sudo=True) 
@task
def deploy_gunicorn(): 
   """
    Upload and configure the supervisord template 
    Store the gunicorn ip_address:port in _deploy.cfg
   """
   destination=join(env.directory,"gunicorn.conf")
   upload_template('deploy/gunicorn.conf',destination,context=env)
@task        
def deploy_conf_files():
    """
    Upload and configure config files such ass local_settings,nginx.conf,supervisord.conf and gunicorn.py
    """
    deploy_local_settings()
    deploy_nginx_conf()
    deploy_supervisor()
    deploy_gunicorn()
    
@task       
def update_site():
    """
    Pull and update, build static and reload gunicorn
    """
    maint_mode()
    pull_update()
    update_requirements()
    migrate()
    build_static()
    production_mode()
