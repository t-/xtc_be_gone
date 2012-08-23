import os 
import sys
import subprocess as sp





def gen_non_water_pdb():
    if not os.path.exists('non_wat.pdb'):
        return
    if not os.path.exists('topol.tpr'):
        raise Exception('topol.tpr file in %s not found' % (root))
    p = sp.Popen("source /home/tgraen/owl/enderlein/env.sh; echo 'editconf -f topol.tpr -o tmp.pdb'", shell=True, stdin=sp.PIPE)
    p.communicate()
    p = sp.Popen("source /home/tgraen/owl/enderlein/env.sh; echo 'trjconv -f tmp.pdb -s topol.tpr -o non_wat.pdb -pbc mol'", shell=True, stdin=sp.PIPE)
    p.communicate("non-Water")

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
    if len(xtclist)==0:
        return
    print 'Found finished .xtc trajectories:', root, xtclist
    
    gen_non_water_pdb()
    
    #non-Water - trjconv -s topol.tpr -f xtclist_item -o traj_out.pdb -pbc mol
    #rm 
    
#-------------------------------------

print 'This is the xtc finder'
cur_dir=os.getcwd()
for root, dirs, files in os.walk('.'):
    os.chdir(root)
    process_dirs(root, files)
    os.chdir(cur_dir)
    