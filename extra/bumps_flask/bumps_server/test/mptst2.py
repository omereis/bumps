import multiprocessing
import asyncio, os

qMain = multiprocessing.Queue()

async def worker(num_q):
    while True:
        n = qMain.get()
        await asyncio.sleep(1.5)
        print (f'Process {os.getpid()}, Worker read {n}:')
        if n < 0:
            break
    return

def worker_manager(num_q):
    asyncio.run(worker(num_q))

async def producer (q):
    for n in range(5):
        qMain.put(n)
        print(f'producer just added {n}')
        await asyncio.sleep(1)
        #await q.put(n)
    #await q.put(-1)
    qMain.put(-1)
    print(f'producer just added -1')

def producer_manager(num_q):
    asyncio.run(producer(num_q))

if __name__ == '__main__':
    jobs = []

    queue = multiprocessing.Queue()
    pReader = multiprocessing.Process(name='reader', target=worker_manager, args=(queue,))
    pWriter = multiprocessing.Process(name='writer', target=producer_manager, args=(queue,))

    jobs.append(pReader)
    jobs.append(pWriter)
    pReader.start()
    pWriter.start()
    for p in jobs:
        p.join()

