import os
import platform
import shutil
from datetime import datetime
import multiprocessing as mp
import scipy.stats
import numpy as np
import matplotlib.pyplot as plt

bin_name = "snesim"
if not platform.platform().lower().startswith("win"):
	bin_name = "./" + bin_name


with open("snesim.par", 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "random number seed" in line.lower():
        print(line)
        break
iline = i
seed_line = lines[iline][10:]
arr_dir = "reals"



def worker(iworker, nreals, seed):
    w_d = str(iworker)
    if os.path.exists(w_d):
        shutil.rmtree(w_d)
    np.random.seed(seed)
    shutil.copytree("template", str(iworker))
    os.chdir(str(iworker))
    for ireal in range(nreals):
        seed = np.random.randint(0, 10000000, size=1)[0]
        print(iworker, ireal, seed)
        lines[iline] = "{0:<10d}".format(seed) + seed_line
        with open("snesim.par", 'w') as f:
            [f.write(line) for line in lines]

        os.system("{0} <snesim.par >nul".format(bin_name))
        nreal = 1
        with open("snesim.out", 'r') as f:
            [f.readline() for _ in range(4)]
            arr = np.loadtxt(f)[:, 0]
        # print(arr.shape)
        arr = arr.reshape((250, 250, nreal))[:, :, 0]
        # arr = arr[:150,:240].transpose()
        # samp = np.zeros((80,50))
        # for ii,i in enumerate(range(0,240,3)):
        # 	for jj,j in enumerate(range(0,150,3)):
        # 		m = scipy.stats.mode(arr[i:i+3,j:j+3],axis=None)[0]
        # 		samp[ii,jj] = m
        arr = arr[:100,:160].transpose()
        samp = np.zeros((80,50))
        for ii,i in enumerate(range(0,160,2)):
        	for jj,j in enumerate(range(0,100,2)):
        		m = scipy.stats.mode(arr[i:i+2,j:j+2],axis=None)[0]
        		samp[ii,jj] = m
        # print(arr.shape)
        np.savetxt(os.path.join("..", arr_dir, "real_{0:05d}_{1:05d}.dat".format(ireal, iworker)), samp, fmt="%1d")
    os.chdir("..")

def draw():
    if os.path.exists(arr_dir):
        shutil.rmtree(arr_dir)
    os.mkdir(arr_dir)
    s = datetime.now()
    nworkers = 20
    nreals = 1000
    procs = []
    for iworker in range(nworkers):
        seed = np.random.randint(0, 1000000, size=1)[0]
        p = mp.Process(target=worker, args=(iworker, nreals, seed))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()

    print("took:", (datetime.now() - s).total_seconds())


def process_draws():
    reals = os.listdir(arr_dir)
    for real in reals:
        arr = np.loadtxt(os.path.join(arr_dir,real))
        # samp = np.zeros((80,50))
        # for ii,i in enumerate(range(0,240,3)):
        # 	for jj,j in enumerate(range(0,150,3)):
        # 		print(scipy.stats.mode(arr[i:i+3,j:j+3],axis=None)[0])
        # 		samp[ii,jj] = scipy.stats.mode(arr[i:i+3,j:j+3],axis=None)[0]
        plt.imshow(arr)
        plt.show()
        break
       


if __name__ == "__main__":
    draw()
    #process_draws()