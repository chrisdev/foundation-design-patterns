from fabric.api import *
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
    env.hosts=['xibalba.chrisdev.com']
    env.directory = join('/usr/local/sites/',PROJECT_PATH)
    env.sites='/usr/local/sites/'
    env.project=PROJECT_PATH
    env.virtualenvs='/home/django/virtualenvs/'
    env.python='/home/django/virtualenvs/%s-env/bin/python' % PROJECT_PATH
    env.user ='django'
@task
def create_virtualenv():
    with settings(warn_only=True):
        if run("test -d %s%s-env" % (env.virtualenvs,env.project)).failed:
            run('mkvirtualenv %s-env' % env.project)
@task   
def clone_project():
    with settings(warn_only=True):
        with cd(env.sites):
            if run("test -d %s%s" % (env.virtualenvs,env.project)).failed:
                run('hg clone ssh://hg@bitbucket.org/chrisdev/%s' % env.project)
 

@task
def enable_site():
    with cd('/etc/nginx/sites-enabled/'):
        with settings(warn_only=True):
            sudo('ln -s /etc/nginx/sites-available/%s %s' % (env.project,env.project))
    sudo('/etc/init.d/nginx configtest')
    
@task        
def bootstrap():
    """Create everting that you need to do to get the project started on this server"""
    create_virtualenv()
    clone_project()
    update_requirements()
    deploy_conf_files()
    migrate()
    with settings(warn_only=True):
        with cd(env.directory):
            run('mkdir logs')
            
    
    
@task    
def virtualenv(command):
    """
    Enable the virtualenv
    """
    with cd(env.directory):
        #'source /usr/local/virtualenvs/caracas_site-env/bin/activate'
        run('source %s%s-env/bin/activate && %s' % (env.virtualenvs,env.project,command))
        

@task       
def pull_update():
    """
    Hg pull and update
    """
    with cd(env.directory):
        run('hg pull')
        run('hg update')
           
@task
def update_requirements():
    """
    Install new requirements if any
    """
    virtualenv('pip install -r requirements/project.txt')  
@task    
def migrate():
    with cd(env.directory):
        run(env.python + " manage.py migrate --all")    
@task   
def syncdb():
    """
    Run the syncdb environment
    """
    with cd(env.directory):
        run(env.python + " manage.py syncdb")
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
    Reload the apache server 
    """
    sudo("/etc/init.d/nginx reload")
@task    
def gunicorn_reload():
    with settings(warn_only=True):
        sudo("sudo supervisorctl restart %s" % PROJECT_PATH)
        

@task       
def nginx_reload():
        
    sudo("/etc/init.d/nginx reload",)
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
    with cd(env.directory):
        run('cp deploy/local_settings.py local_settings.py')  
@task       
def deploy_nginx_conf():
    with cd(env.directory):
        sudo('cp deploy/nginx.conf /etc/nginx/sites-available/%s' % env.project)    
@task        
def deploy_supervisor_conf():
    with cd(env.directory):
        sudo ('cp deploy/supervisor.conf /etc/supervisor/conf.d/%s.conf' % env.project)    
@task        
def deploy_conf_files():
    deploy_local_settings()
    deploy_nginx_conf()
    deploy_supervisor_conf()
    
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
