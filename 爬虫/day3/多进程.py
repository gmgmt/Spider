from multiprocessing import Pool
import os, time, random

def long_time_task(name):
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))

if __name__=='__main__':
    #  4一般代表电脑核数
    p = Pool(4)
    for i in range(5):
        p.apply_async(long_time_task, args=(i,))
    p.close()
    p.join()
