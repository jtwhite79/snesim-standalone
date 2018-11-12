import os
import shutil
from datetime import datetime
import multiprocessing as mp
import numpy as np
import matplotlib.pyplot as plt

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

        os.system("./snesim <snesim.par >nul")
        nreal = 1
        with open("snesim.out", 'r') as f:
            [f.readline() for _ in range(4)]
            arr = np.loadtxt(f)[:, 0]
        # print(arr.shape)
        arr = arr.reshape((250, 250, nreal))[:, :, 0]
        # print(arr.shape)
        np.savetxt(os.path.join("..", arr_dir, "real_{0:05d}_{1:05d}.dat".format(ireal, iworker)), arr, fmt="%1d")
    os.chdir("..")

def draw():
    if os.path.exists(arr_dir):
        shutil.rmtree(arr_dir)
    os.mkdir(arr_dir)
    s = datetime.now()
    nworkers = 7
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
        plt.imshow(arr)
        plt.show()
        break


if __name__ == "__main__":
    process_draws()