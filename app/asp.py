

t = 0
def quic_sort(lst: list) -> list:
    global t
    t += 1
    if len(lst) <= 1:
        return lst
    
    pivot = lst[len(lst) // 2]
    
    left = []
    middle = []
    right = []
    for i in lst:
        if i < pivot:
            left.append(i)
        elif i == pivot:
            middle.append(i)
        else:
            right.append(i)
            
    return quic_sort(left) + middle + quic_sort(right)
    

l = [12, 323, 1, 2, 5, 432, 332, 1, 2, 424]
r = quic_sort(l)
print(t)
print(r)























# def buble_sort(lst: list):
    
#     total = len(lst)
#     t = 0
#     for i in range(total):
#         stop = False
#         for j in range(total - i - 1):
            
#             if lst[j] > lst[j+1]:
#                 lst[j], lst[j+1] = lst[j+1], lst[j]
#                 t += 1
#                 # stop = True
            
            
#         # if stop is False:
#         #     break
#     print(t)
#     return lst
            
            
    
# l = [2, 4, 1, 2, 4, 2, 6, 3, 4, 2, 8, 2, 4, 90, 43]
# rv = buble_sort(l)
# print(rv)