a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
b = [1, 2, 3, 4, 5]

diff = len(a) - len(b)

for i in range(len(b) -1, -1, -1):
    print(f"{a[i+diff]} = {b[i]}")
