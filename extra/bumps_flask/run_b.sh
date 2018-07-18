#!/bin/bash

#SBATCH --time=00:30:00
#SBATCH job-name=sfb
#SBATCH --ntasks=2
#SBATCH --mem-per-cpu=512M

#celery -A bumps worker -E -l info -n bumps -Q bumps_queue

#from bumps import cli
#import sys

# sys.argv=['','/home/bumps_user/bumps_flask/test/cf1.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/results', '--fit=newton']
# cli.main()
# cli.main(['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf1.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/results', '--fit=newton'])
# cli.main(['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf2.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/results', '--fit=newton'])
# cli.main.delay(['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf1.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/results', '--fit=newton'])
# cli.main.delay(['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf2.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/results', '--fit=newton'])
# tasks.run_bumps(['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf2.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/results', '--fit=newton'])
# tasks.run_bumps.delay(['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf2.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/bumps_flask/results', '--fit=newton'])
# res=tasks.run_bumps.delay(['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf2.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/bumps_flask/results', '--fit=newton'])

['/usr/local/lib/python2.7/dist-packages/bumps/cli.py','/home/bumps_user/bumps_flask/test/cf2.py', '--batch', '--stepmon', '--burn=100', '--steps=100', '--store=/home/bumps_user/results', '--fit=newton']

python -m bumps.cli /home/bumps_user/bumps_flask/test/cf1.py --batch --stepmon --burn=100 --steps=100 --store=/home/bumps_user/results --fit=newton

celeryMain(args, args, ...)
sys.argv = ()
main()

celery multi start 10 -A celery_bumps -l info -Q:1-3 images,video -Q:4,5 data -Q default -L:4,5 debug
<!--
    <bottom>
    {% include 'bottom_html.html' %}
</bottom>
-->

    language = SelectField('Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')]
