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
        self.ftpcon = False
        self.getFTPConnection()
        self.ftp_cur_dir = self.ftpcon.pwd()
        
    def getFTPConnection(self):
        if self.ftpcon:
            print '### Reinitializing the ftp connection'
            try:
                self.ftpcon.quit()
            except Exception:
                print 'Error trying to disconnect from the ftp'
        else:
            print '### Initializing the ftp connection'
        self.ftpcon = FTP()
        self.ftpcon.connect('archiv105',1021)
        self.ftpcon.login(getuser(),self.ftppasswd)
    
    def gen_non_water_pdb(self,root):
        if os.path.exists('%s.pdb'%(self.GLOBAL_xtcgroup)):
            return
        if not os.path.exists('topol.tpr'):
            raise Exception('topol.tpr file in %s not found' % (root))
        print '\nGenerating %s pdb structure' %(self.GLOBAL_xtcgroup)
        p = sp.Popen("source /home/tgraen/owl/enderlein/env.sh; editconf -f topol.tpr -o tmp.pdb", shell=True, stdin=sp.PIPE, stdout = sp.PIPE, stderr = sp.PIPE)
        sto,ste=p.communicate()
        p = sp.Popen("source /home/tgraen/owl/enderlein/env.sh; trjconv -f tmp.pdb -s topol.tpr -o %s.pdb -pbc mol" % (self.GLOBAL_xtcgroup), shell=True, stdin=sp.PIPE, stdout = sp.PIPE, stderr = sp.PIPE)
        sto,ste=p.communicate(self.GLOBAL_xtcgroup)
        os.remove('tmp.pdb')
        #store file on archive
        self.getFTPConnection()
        self.change_dir_ftp(root)
        print '\tftp: Storing file %s.pdb in %s\n'%(self.GLOBAL_xtcgroup,root)
        f=file('%s.pdb'%(self.GLOBAL_xtcgroup),'rb')
        self.ftpcon.storbinary('STOR %s.pdb'%(self.GLOBAL_xtcgroup),f)
    
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
                pass
            self.ftpcon.cwd(dirname)
            print '\tftp:\tchanged to directory', self.ftpcon.pwd()
    
    def convert_xtc_file(self, xtc_filename):
        print '## Processing', xtc_filename
        small_xtc_filename = xtc_filename.replace('traj', self.GLOBAL_xtcgroup)
        p = sp.Popen("source /home/tgraen/owl/enderlein/env.sh; trjconv -s topol.tpr -f %s -o %s -pbc mol" % (xtc_filename, small_xtc_filename), shell=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        sto, ste = p.communicate(self.GLOBAL_xtcgroup)
        print sto
        print ste
        return small_xtc_filename

    def ftp_upload_xtc(self, root, fileName):
        self.change_dir_ftp(root)
        f = file(fileName, 'rb')
        print '\tftp: Storing file %s in %s\n' % (fileName, root)
        self.ftpcon.storbinary('STOR ' + fileName, f)
        print 'Existing backups in folder %s:' % (root), self.ftpcon.nlst()
        #self.ftpcon.cwd(self.ftp_cur_dir)
        #print '\tftp changing back to',self.ftpcon.pwd()

    def process_xtc_file(self, root, xtc_filename):
        small_xtc_filename = self.convert_xtc_file(xtc_filename)
        self.getFTPConnection()
        self.ftp_upload_xtc(root, small_xtc_filename)


    def process_dirs(self,root, files):
        if not root.endswith('04-md'):
            return 

        xtclist = self.gen_xtc_list(files)
        if len(xtclist) == 0:
            return
        print '\n#Good: Found finished .xtc_filename trajectories:', root, xtclist
        
        self.gen_non_water_pdb(root)
        
        for xtc_filename in xtclist:
            self.process_xtc_file(root, xtc_filename)
            


#-------------------------------------
def main():
    store = store_xtc_files()
    
    print '\n\nThis is the xtc backup speaking'
    cur_dir = os.getcwd()
    for root, dirs, files in os.walk('.'):
        os.chdir(root)
        store.process_dirs(root, files)
        os.chdir(cur_dir)
    print 'Normal Termination\n'
    
if __name__ == '__main__':
    main()