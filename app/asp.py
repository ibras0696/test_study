
# buble sort
def bble_sort(lst):
    
    total = len(lst)
    for i in range(total):
        for j in range(0, total - i - 1):
            if lst[j] > lst[j+1]:
                lst[j], lst[j+1] = lst[j+1], lst[j]
                
    
    return lst


l = [4, 2, 3, 1]
print(bble_sort(l))

def quick_sort(arr):
    
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot] 
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
    


l2 = [4, 2, 5, 6, 1, 3, 4]
print(quick_sort(l2))