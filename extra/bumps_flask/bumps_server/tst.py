class Job:
    id = None
    def __init__ (self, num):
        self.id = num

IDs = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
listJobs = []
for id in IDs:
    listJobs.append(Job(id))

for n in range(len(listJobs)):
    print(f'index {n}, id: {listJobs[n].id}')

delIdx = ['5', '10']

n = 0
while n < len(listJobs):
    if str(listJobs[n].id) in delIdx:
        listJobs.pop(n)
    else:
        n += 1

print('\nafter deleting')
for n in range(len(listJobs)):
    print(f'index {n}, id: {listJobs[n].id}')
