#!/usr/bin/env python

import os 
import subprocess as sp

def myPopen(cmd,inputstr=None):
    p = sp.Popen(cmd,shell=True, stdin=sp.PIPE)
    if inputstr==None:
        p.communicate()
    else:
        p.communicate(inputstr)
    if p.returncode != 0:
        raise Exception("Command %s failed with non zero return code %d."%(cmd,p.returncode))
    
def myPopenOutput(cmd,inputstr=None):
    p = sp.Popen(cmd,shell=True, stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.PIPE)
    if inputstr==None:
        out,err = p.communicate()
        
    else:
        out,err = p.communicate(inputstr)
    if p.returncode != 0:
        print out,err
        raise Exception("Command %s failed with non zero return code %d."%(cmd,p.returncode))

    return (out,err)

class gen_new_runs():
    def __init__(self):
        self.GLOBAL_xtcgroup = 'non-Water'
    
    def gen_trr_list(self,files):
        trrlist = []
        for datei in files:
            if datei.endswith('.trr') and datei.startswith("traj"):
                trrlist.append(datei)
        trrlist.sort()
        return trrlist

    def process_dirs(self,root, files):
        if not root.endswith('04-md'):
            return 
        print '######',root,files
        trrlist = self.gen_trr_list(files)
        
        myPopen("source /netmount/bluearc/tgraen/env.sh; rm -rf ../05-md; mkdir ../05-md; cd ../05-md/; cp ../04-md/topol.top ../04-md/input.pdb .")
        if len(trrlist) == 0:            
            myPopen("source /netmount/bluearc/tgraen/env.sh; cd ../05-md; grompp -f $PROJHOME/params/md.mdp -c input.pdb")
        else:
            out,err = myPopenOutput("source /netmount/bluearc/tgraen/env.sh; cd ../05-md; cp $PROJHOME/params/md-no_vel.mdp .; grompp -f md-no_vel.mdp -c input.pdb -t ../04-md/%s -o dummy.tpr -v"%trrlist[-1])
            for line in err.split("\n"):
                if line.startswith("Using frame at t"):
                    step=int(line.strip().split()[-2])
            print "step to set is",step
            myPopen("source /netmount/bluearc/tgraen/env.sh; cd ../05-md; sed -i \"s/987654321/%d/\" md-no_vel.mdp;grompp -f md-no_vel.mdp -c input.pdb -t ../04-md/%s"%(step,trrlist[-1]))
        
            

#-------------------------------------
def main():
    store = gen_new_runs()
    
    print '\n\nThis is the xtc backup speaking'
    cur_dir = os.getcwd()
    for root, dirs, files in os.walk('.'):
        os.chdir(root)
        store.process_dirs(root, files)
        os.chdir(cur_dir)
    print 'Normal Termination\n'
    
if __name__ == '__main__':
    main()