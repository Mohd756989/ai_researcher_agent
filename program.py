def two_sum(nums:list,target:int):
    hash_map = {}
    
    for i ,num in enumerate(nums):
        diff = target - num
        
        if diff in hash_map:
            return [hash_map[diff],i]

        hash_map[num] = i
        
# arr = [1,6,2,8,10,4]
# target = 16
# print(two_sum(arr,target))

import heapq

import heapq

def topKFrequent(nums, k):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    heap = []

    for count ,num in freq.items():
        heapq.heappush(heap, (num, count))

        if len(heap) > k:
            heapq.heappop(heap)

    return [num for count, num in heap]
    
arr = [1,1,2,9,3,3,3,5]
k = 2
# print(topKFrequent(arr,k))

# print(True  or False)

#kadane algorithm

def subarray_max(nums):
    current_sum = max_sum = nums[0]
    
    for num in nums[1:]:
        current_sum = max(num,current_sum+num)
        max_sum = max(max_sum,current_sum)
        
    return max_sum

arr = [4, -1, 2, 1]
print(subarray_max(arr)) #the time complexity for this algorithm is O(n)
# def kadane(arr):
#     current_sum = arr[0]
#     max_sum = arr[0]

#     for i in range(1, len(arr)):
#         current_sum = max(arr[i], current_sum + arr[i])
#         max_sum = max(max_sum, current_sum)

#     return max_sum

# arr = [4, -1, 2, 1]
# print(kadane(arr))   # 6



def median(num1,num2):
    num = num1+num2
    
    num.sort()
    length = len(num)
    sum= 0
    for n in num:
        sum += n
    med = sum / length
    
    return med
num1 = [1,2]
num2 = [3,4]
print(median(num1,num2))