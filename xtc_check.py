#!/usr/bin/env python

import os 
import sys
import subprocess as sp
from ftplib import FTP
from getpass import getpass,getuser

class store_xtc_files():
    def __init__(self):
        self.GLOBAL_xtcgroup = 'non-Water'
        print "Enter archive ftp password for user %s"%getuser()
        self.ftppasswd = getpass()
        self.ftpcon = self.getFTPConnection()
        self.ftp_cur_dir = self.ftpcon.pwd()
        
    def getFTPConnection(self):
        conn = FTP()
        conn.connect('archiv105',1021)
        conn.login(getuser(),self.ftppasswd)
        return conn
    
    def gen_non_water_pdb(self):
        if os.path.exists('%s.pdb'%(self.GLOBAL_xtcgroup)):
            return
        if not os.path.exists('topol.tpr'):
            raise Exception('topol.tpr file in %s not found' % (root))
        print 'Generating %s pdb structure' %(self.GLOBAL_xtcgroup)
        p = sp.Popen("source /home/tgraen/owl/enderlein/env.sh; echo ' editconf -f topol.tpr -o tmp.pdb'", shell=True, stdin=sp.PIPE)
        p.communicate()
        p = sp.Popen("source /home/tgraen/owl/enderlein/env.sh; echo ' trjconv -f tmp.pdb -s topol.tpr -o %s.pdb -pbc mol'" % (self.GLOBAL_xtcgroup), shell=True, stdin=sp.PIPE)
        p.communicate(self.GLOBAL_xtcgroup)
        #os.remove('tmp.pdb')
    
    def gen_xtc_list(self,files):
        xtclist = []
        for datei in files:
            if datei.endswith('.xtc'):
                xtclist.append(datei)
        xtclist.sort()
        xtclist = xtclist[:-1]
        return xtclist
    

    def change_dir_ftp(self, root):
        dirs = root.split('/')
        for dirname in dirs[1:]:
            try:
                self.ftpcon.mkd(dirname)
            except Exception:
                ems = 'it did not work, who cares'
            self.ftpcon.cwd(dirname)
            print '\tftp changing to', self.ftpcon.pwd()

    def process_dirs(self,root, files):
        if not root.endswith('04-md'):
            return 
        xtclist = self.gen_xtc_list(files)
        if len(xtclist) == 0:
            return
        print 'Good: Found finished .xtc trajectories:', root, xtclist
        
        self.gen_non_water_pdb()
        
        for xtc in xtclist:
            print 'Processing',xtc
            small_xtc = xtc.replace('traj', self.GLOBAL_xtcgroup)
            p = sp.Popen("source /home/tgraen/owl/enderlein/env.sh; echo ' trjconv -s topol.tpr -f %s -o %s -pbc mol'" % (xtc, small_xtc), shell=True, stdin=sp.PIPE)
            p.communicate(self.GLOBAL_xtcgroup)
            
            self.change_dir_ftp(root)
            
            fileName="topol.tpr"
            f=file(fileName,'rb')
            self.ftpcon.storbinary('STOR '+fileName,f)
            print 'Existing backups in folder %s:'%(root),self.ftpcon.nlst()
            self.ftpcon.cwd(self.ftp_cur_dir)
            print '\tftp changing back to',self.ftpcon.pwd()
            sys.exit(1)

#-------------------------------------
def main():
    store = store_xtc_files()
    
    print 'This is the xtc finder'
    cur_dir = os.getcwd()
    for root, dirs, files in os.walk('.'):
        os.chdir(root)
        store.process_dirs(root, files)
        os.chdir(cur_dir)

if __name__ == '__main__':
    main()