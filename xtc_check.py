#!/usr/bin/env python

import os 
import sys
import subprocess as sp
from ftplib import FTP
from getpass import getpass,getuser

ftpfilenames=["a",]


def getFiles(ftpstr):
    global ftpfilenames
    for i in ftpstr.split():
        ftpfilenames.append(i) 
    ftpfilenames.append("b")
    
    

def getFTPConnection():
    print "Enter archive ftp password for user %s"%getuser()
    ftppasswd = getpass()
    conn = FTP()
    conn.connect('archiv105',1021)
    conn.login(getuser(),ftppasswd)
    return conn

GLOBAL_xtcgroup = 'non-Water'

def gen_non_water_pdb():
    if os.path.exists('%s.pdb'%(GLOBAL_xtcgroup)):
        return
    if not os.path.exists('topol.tpr'):
        raise Exception('topol.tpr file in %s not found' % (root))
    print 'Generating %s pdb structure' %(GLOBAL_xtcgroup)
    p = sp.Popen("source /home/tgraen/owl/enderlein/env.sh; echo ' editconf -f topol.tpr -o tmp.pdb'", shell=True, stdin=sp.PIPE)
    p.communicate()
    p = sp.Popen("source /home/tgraen/owl/enderlein/env.sh; echo ' trjconv -f tmp.pdb -s topol.tpr -o %s.pdb -pbc mol'" % (GLOBAL_xtcgroup), shell=True, stdin=sp.PIPE)
    p.communicate(GLOBAL_xtcgroup)
    #os.remove('tmp.pdb')

def gen_xtc_list(files):
    xtclist = []
    for datei in files:
        if datei.endswith('.xtc'):
            xtclist.append(datei)
    
    xtclist.sort()
    xtclist = xtclist[:-1]
    return xtclist

def process_dirs(root, files):
    if not root.endswith('04-md'):
        return 
    xtclist = gen_xtc_list(files)
    if len(xtclist) == 0:
        return
    print 'Found finished .xtc trajectories:', root, xtclist
    
    gen_non_water_pdb()
    
    for xtc in xtclist:
        print 'Processing',xtc
        p = sp.Popen("source /home/tgraen/owl/enderlein/env.sh; echo ' trjconv -s topol.tpr -f %s -o %s -pbc mol'" % (xtc, xtc.replace('traj', GLOBAL_xtcgroup)), shell=True, stdin=sp.PIPE)
        p.communicate(GLOBAL_xtcgroup)
        
        fileName="topol.tpr"
        f=file(fileName,'rb')
        ftpcon.storbinary('STOR '+fileName,f)
        print ftpcon.dir()
        print ftpcon.retrlines("NLST",getFiles)
        print ftpfilenames
        sys.exit(1)

#-------------------------------------

ftpcon = getFTPConnection()
ftp_cur_dir = ftpcon.pwd()

print 'This is the xtc finder'
cur_dir = os.getcwd()
for root, dirs, files in os.walk('.'):
    os.chdir(root)
    process_dirs(root, files)
    os.chdir(cur_dir)
    
