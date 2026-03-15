"""
dsa_problems.py — problem bank, rotates daily by date hash
"""

import hashlib

PROBLEMS = [
    {
        "slug": "two_sum",
        "title": "Two Sum",
        "difficulty": "Easy",
        "topic": "Arrays / Hash Map",
        "description": "Given an array of integers nums and an integer target,\nreturn indices of the two numbers that add up to target.\nYou may assume exactly one solution exists.",
        "examples": [
            "Input: nums = [2,7,11,15], target = 9  →  Output: [0,1]",
            "Input: nums = [3,2,4], target = 6       →  Output: [1,2]",
        ],
        "fn_name": "two_sum",
        "params": "nums: list[int], target: int",
        "approach": "Use a hash map to store each number's index as we iterate.\nFor each num, check if (target - num) already exists in the map.",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
        "solution": """\
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []""",
        "test_cases": [
            "two_sum([2,7,11,15], 9)  == [0,1]",
            "two_sum([3,2,4], 6)      == [1,2]",
            "two_sum([3,3], 6)        == [0,1]",
        ],
    },
    {
        "slug": "best_time_buy_sell_stock",
        "title": "Best Time to Buy and Sell Stock",
        "difficulty": "Easy",
        "topic": "Arrays / Greedy",
        "description": "Given an array prices where prices[i] is the price on day i,\nreturn the maximum profit from one buy-sell transaction.\nReturn 0 if no profit is possible.",
        "examples": [
            "Input: [7,1,5,3,6,4]  →  Output: 5  (buy@1, sell@6)",
            "Input: [7,6,4,3,1]    →  Output: 0  (prices only fall)",
        ],
        "fn_name": "max_profit",
        "params": "prices: list[int]",
        "approach": "Track the minimum price seen so far.\nAt each step compute profit = current - min_price, update best profit.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "solution": """\
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    return max_profit""",
        "test_cases": [
            "max_profit([7,1,5,3,6,4]) == 5",
            "max_profit([7,6,4,3,1])   == 0",
            "max_profit([1,2])         == 1",
        ],
    },
    {
        "slug": "valid_parentheses",
        "title": "Valid Parentheses",
        "difficulty": "Easy",
        "topic": "Stack",
        "description": "Given a string s containing '(', ')', '{', '}', '[', ']',\ndetermine if the input string is valid.\nOpen brackets must be closed in the correct order.",
        "examples": [
            "Input: '()'      →  Output: True",
            "Input: '()[]{}'  →  Output: True",
            "Input: '(]'      →  Output: False",
        ],
        "fn_name": "is_valid",
        "params": "s: str",
        "approach": "Use a stack. Push open brackets; on closing bracket,\ncheck if top of stack is the matching opener.",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
        "solution": """\
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for ch in s:
        if ch in mapping:
            top = stack.pop() if stack else '#'
            if mapping[ch] != top:
                return False
        else:
            stack.append(ch)
    return not stack""",
        "test_cases": [
            "is_valid('()')      == True",
            "is_valid('()[]{}'   == True",
            "is_valid('(]')      == False",
        ],
    },
    {
        "slug": "climbing_stairs",
        "title": "Climbing Stairs",
        "difficulty": "Easy",
        "topic": "Dynamic Programming",
        "description": "You are climbing a staircase with n steps.\nEach time you can climb 1 or 2 steps.\nIn how many distinct ways can you climb to the top?",
        "examples": [
            "Input: n = 2  →  Output: 2  (1+1, 2)",
            "Input: n = 3  →  Output: 3  (1+1+1, 1+2, 2+1)",
        ],
        "fn_name": "climb_stairs",
        "params": "n: int",
        "approach": "Classic Fibonacci pattern. ways(n) = ways(n-1) + ways(n-2).\nUse two variables to avoid O(n) space.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "solution": """\
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b""",
        "test_cases": [
            "climb_stairs(1) == 1",
            "climb_stairs(2) == 2",
            "climb_stairs(5) == 8",
        ],
    },
    {
        "slug": "merge_sorted_arrays",
        "title": "Merge Sorted Array",
        "difficulty": "Easy",
        "topic": "Two Pointers",
        "description": "Merge nums2 into nums1 in-place. nums1 has length m+n\nwhere last n elements are 0 placeholders.",
        "examples": [
            "nums1=[1,2,3,0,0,0] m=3, nums2=[2,5,6] n=3  →  [1,2,2,3,5,6]",
            "nums1=[1] m=1, nums2=[] n=0                  →  [1]",
        ],
        "fn_name": "merge",
        "params": "nums1: list[int], m: int, nums2: list[int], n: int",
        "approach": "Fill from the back. Use three pointers: end of nums1 data,\nend of nums2, and end of total array. Avoids shifting.",
        "time_complexity": "O(m+n)",
        "space_complexity": "O(1)",
        "solution": """\
    p1, p2, p = m - 1, n - 1, m + n - 1
    while p1 >= 0 and p2 >= 0:
        if nums1[p1] > nums2[p2]:
            nums1[p] = nums1[p1]
            p1 -= 1
        else:
            nums1[p] = nums2[p2]
            p2 -= 1
        p -= 1
    nums1[:p2 + 1] = nums2[:p2 + 1]""",
        "test_cases": [
            "merge([1,2,3,0,0,0],3,[2,5,6],3) → [1,2,2,3,5,6]",
            "merge([1],1,[],0)                 → [1]",
        ],
    },
    {
        "slug": "reverse_linked_list",
        "title": "Reverse Linked List",
        "difficulty": "Easy",
        "topic": "Linked List",
        "description": "Given the head of a singly linked list, reverse the list\nand return the reversed list's head.",
        "examples": [
            "Input: 1→2→3→4→5  →  Output: 5→4→3→2→1",
            "Input: 1→2         →  Output: 2→1",
        ],
        "fn_name": "reverse_list",
        "params": "head",
        "approach": "Iterative: maintain prev=None, curr=head.\nAt each step: save next, point curr.next to prev, advance both.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "solution": """\
    prev, curr = None, head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev""",
        "test_cases": [
            "reverse_list([1,2,3,4,5]) == [5,4,3,2,1]",
            "reverse_list([1,2])       == [2,1]",
        ],
    },
    {
        "slug": "maximum_subarray",
        "title": "Maximum Subarray (Kadane's Algorithm)",
        "difficulty": "Medium",
        "topic": "Arrays / DP",
        "description": "Given an integer array nums, find the subarray\nwith the largest sum and return its sum.",
        "examples": [
            "Input: [-2,1,-3,4,-1,2,1,-5,4]  →  Output: 6  (subarray [4,-1,2,1])",
            "Input: [1]                        →  Output: 1",
        ],
        "fn_name": "max_sub_array",
        "params": "nums: list[int]",
        "approach": "Kadane's: track current running sum.\nIf adding next element is worse than starting fresh, reset to that element.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "solution": """\
    max_sum = curr = nums[0]
    for num in nums[1:]:
        curr = max(num, curr + num)
        max_sum = max(max_sum, curr)
    return max_sum""",
        "test_cases": [
            "max_sub_array([-2,1,-3,4,-1,2,1,-5,4]) == 6",
            "max_sub_array([1])                      == 1",
            "max_sub_array([-1])                     == -1",
        ],
    },
    {
        "slug": "binary_search",
        "title": "Binary Search",
        "difficulty": "Easy",
        "topic": "Binary Search",
        "description": "Given a sorted array of distinct integers and a target,\nreturn its index or -1 if not found. Must be O(log n).",
        "examples": [
            "Input: nums=[-1,0,3,5,9,12], target=9  →  Output: 4",
            "Input: nums=[-1,0,3,5,9,12], target=2  →  Output: -1",
        ],
        "fn_name": "search",
        "params": "nums: list[int], target: int",
        "approach": "Classic binary search. Maintain lo and hi pointers.\nCheck mid; shrink window based on comparison with target.",
        "time_complexity": "O(log n)",
        "space_complexity": "O(1)",
        "solution": """\
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1""",
        "test_cases": [
            "search([-1,0,3,5,9,12], 9) == 4",
            "search([-1,0,3,5,9,12], 2) == -1",
        ],
    },
    {
        "slug": "number_of_islands",
        "title": "Number of Islands",
        "difficulty": "Medium",
        "topic": "BFS / DFS / Graph",
        "description": "Given an m×n grid of '1' (land) and '0' (water),\nreturn the number of islands.",
        "examples": [
            "grid with one big land mass  →  1",
            "grid with four isolated cells  →  4",
        ],
        "fn_name": "num_islands",
        "params": "grid: list[list[str]]",
        "approach": "DFS flood-fill: for each unvisited '1', increment count\nand DFS to mark all connected land as visited ('0').",
        "time_complexity": "O(m*n)",
        "space_complexity": "O(m*n) recursion stack",
        "solution": """\
    if not grid:
        return 0
    count = 0
    def dfs(r, c):
        if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]) or grid[r][c] != '1':
            return
        grid[r][c] = '0'
        dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1)
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)
    return count""",
        "test_cases": [
            "num_islands([['1','1','0'],['0','1','0'],['0','0','1']]) == 2",
            "num_islands([['1','1','1'],['1','1','1']]) == 1",
        ],
    },
    {
        "slug": "longest_common_prefix",
        "title": "Longest Common Prefix",
        "difficulty": "Easy",
        "topic": "Strings",
        "description": "Write a function to find the longest common prefix string\namongst an array of strings. Return '' if none.",
        "examples": [
            "Input: ['flower','flow','flight']  →  Output: 'fl'",
            "Input: ['dog','racecar','car']     →  Output: ''",
        ],
        "fn_name": "longest_common_prefix",
        "params": "strs: list[str]",
        "approach": "Sort the list. The common prefix of the whole list\nequals the common prefix of the first and last strings.",
        "time_complexity": "O(n log n + m) where m = prefix length",
        "space_complexity": "O(1)",
        "solution": """\
    if not strs:
        return ''
    strs.sort()
    first, last = strs[0], strs[-1]
    i = 0
    while i < len(first) and i < len(last) and first[i] == last[i]:
        i += 1
    return first[:i]""",
        "test_cases": [
            "longest_common_prefix(['flower','flow','flight']) == 'fl'",
            "longest_common_prefix(['dog','racecar','car'])    == ''",
        ],
    },
    {
        "slug": "valid_anagram",
        "title": "Valid Anagram",
        "difficulty": "Easy",
        "topic": "Strings / Hash Map",
        "description": "Given two strings s and t, return True if t is an anagram of s.",
        "examples": [
            "Input: s='anagram', t='nagaram'  →  True",
            "Input: s='rat', t='car'          →  False",
        ],
        "fn_name": "is_anagram",
        "params": "s: str, t: str",
        "approach": "Count character frequencies with a dict (or Counter).\nCompare the two frequency maps.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1) — at most 26 keys",
        "solution": """\
    if len(s) != len(t):
        return False
    from collections import Counter
    return Counter(s) == Counter(t)""",
        "test_cases": [
            "is_anagram('anagram','nagaram') == True",
            "is_anagram('rat','car')         == False",
        ],
    },
    {
        "slug": "product_except_self",
        "title": "Product of Array Except Self",
        "difficulty": "Medium",
        "topic": "Arrays / Prefix Product",
        "description": "Given integer array nums, return array answer where\nanswer[i] = product of all elements except nums[i].\nMust run in O(n) without using division.",
        "examples": [
            "Input: [1,2,3,4]  →  Output: [24,12,8,6]",
            "Input: [-1,1,0,-3,3]  →  Output: [0,0,9,0,0]",
        ],
        "fn_name": "product_except_self",
        "params": "nums: list[int]",
        "approach": "Two passes: left pass fills prefix products,\nright pass multiplies suffix products into result.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1) output array excluded",
        "solution": """\
    n = len(nums)
    res = [1] * n
    prefix = 1
    for i in range(n):
        res[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):
        res[i] *= suffix
        suffix *= nums[i]
    return res""",
        "test_cases": [
            "product_except_self([1,2,3,4])    == [24,12,8,6]",
            "product_except_self([2,3])        == [3,2]",
        ],
    },
    {
        "slug": "contains_duplicate",
        "title": "Contains Duplicate",
        "difficulty": "Easy",
        "topic": "Arrays / Hash Set",
        "description": "Given integer array nums, return True if any value\nappears at least twice, False if all elements are distinct.",
        "examples": [
            "Input: [1,2,3,1]     →  True",
            "Input: [1,2,3,4]     →  False",
        ],
        "fn_name": "contains_duplicate",
        "params": "nums: list[int]",
        "approach": "Add each element to a set. If element already in set → duplicate found.",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
        "solution": """\
    seen = set()
    for n in nums:
        if n in seen:
            return True
        seen.add(n)
    return False""",
        "test_cases": [
            "contains_duplicate([1,2,3,1]) == True",
            "contains_duplicate([1,2,3,4]) == False",
        ],
    },
    {
        "slug": "find_minimum_rotated_array",
        "title": "Find Minimum in Rotated Sorted Array",
        "difficulty": "Medium",
        "topic": "Binary Search",
        "description": "Given a rotated sorted array of unique elements,\nfind the minimum element. Must run in O(log n).",
        "examples": [
            "Input: [3,4,5,1,2]    →  Output: 1",
            "Input: [4,5,6,7,0,1,2] →  Output: 0",
        ],
        "fn_name": "find_min",
        "params": "nums: list[int]",
        "approach": "Binary search: if mid > right, minimum is in right half.\nOtherwise minimum is in left half (including mid).",
        "time_complexity": "O(log n)",
        "space_complexity": "O(1)",
        "solution": """\
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]""",
        "test_cases": [
            "find_min([3,4,5,1,2])     == 1",
            "find_min([4,5,6,7,0,1,2]) == 0",
            "find_min([11,13,15,17])   == 11",
        ],
    },
    {
        "slug": "majority_element",
        "title": "Majority Element",
        "difficulty": "Easy",
        "topic": "Arrays / Boyer-Moore Voting",
        "description": "Given array nums of size n, return the majority element.\nThe majority element appears more than n/2 times.",
        "examples": [
            "Input: [3,2,3]        →  Output: 3",
            "Input: [2,2,1,1,1,2,2] →  Output: 2",
        ],
        "fn_name": "majority_element",
        "params": "nums: list[int]",
        "approach": "Boyer-Moore Voting: maintain a candidate and count.\nWhen count hits 0, switch candidate. Majority always survives.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "solution": """\
    candidate, count = None, 0
    for num in nums:
        if count == 0:
            candidate = num
        count += (1 if num == candidate else -1)
    return candidate""",
        "test_cases": [
            "majority_element([3,2,3])         == 3",
            "majority_element([2,2,1,1,1,2,2]) == 2",
        ],
    },
    {
        "slug": "missing_number",
        "title": "Missing Number",
        "difficulty": "Easy",
        "topic": "Arrays / Math",
        "description": "Given array nums with n distinct numbers in range [0,n],\nreturn the one number missing from the range.",
        "examples": [
            "Input: [3,0,1]     →  Output: 2",
            "Input: [0,1]       →  Output: 2",
        ],
        "fn_name": "missing_number",
        "params": "nums: list[int]",
        "approach": "Expected sum of 0..n is n*(n+1)//2. Subtract actual sum.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "solution": """\
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)""",
        "test_cases": [
            "missing_number([3,0,1])               == 2",
            "missing_number([0,1])                 == 2",
            "missing_number([9,6,4,2,3,5,7,0,1])  == 8",
        ],
    },
    {
        "slug": "rotate_array",
        "title": "Rotate Array",
        "difficulty": "Medium",
        "topic": "Arrays",
        "description": "Given an integer array nums, rotate it to the right by k steps.\nDo it in-place with O(1) extra space.",
        "examples": [
            "nums=[1,2,3,4,5,6,7], k=3  →  [5,6,7,1,2,3,4]",
            "nums=[-1,-100,3,99], k=2   →  [3,99,-1,-100]",
        ],
        "fn_name": "rotate",
        "params": "nums: list[int], k: int",
        "approach": "Three-reversal trick: reverse all, reverse first k, reverse rest.\nHandle k > n with k = k % n.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "solution": """\
    n = len(nums)
    k %= n
    def rev(l, r):
        while l < r:
            nums[l], nums[r] = nums[r], nums[l]
            l += 1; r -= 1
    rev(0, n-1); rev(0, k-1); rev(k, n-1)""",
        "test_cases": [
            "rotate([1,2,3,4,5,6,7],3) → [5,6,7,1,2,3,4]",
            "rotate([-1,-100,3,99],2)  → [3,99,-1,-100]",
        ],
    },
    {
        "slug": "palindrome_number",
        "title": "Palindrome Number",
        "difficulty": "Easy",
        "topic": "Math",
        "description": "Given an integer x, return True if it's a palindrome.\nNegative numbers are not palindromes.",
        "examples": [
            "Input: 121   →  True",
            "Input: -121  →  False",
            "Input: 10    →  False",
        ],
        "fn_name": "is_palindrome",
        "params": "x: int",
        "approach": "Reverse only the second half of digits.\nCompare reversed half with first half.",
        "time_complexity": "O(log n)",
        "space_complexity": "O(1)",
        "solution": """\
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    rev = 0
    while x > rev:
        rev = rev * 10 + x % 10
        x //= 10
    return x == rev or x == rev // 10""",
        "test_cases": [
            "is_palindrome(121)  == True",
            "is_palindrome(-121) == False",
            "is_palindrome(10)   == False",
        ],
    },
    {
        "slug": "fizz_buzz",
        "title": "FizzBuzz",
        "difficulty": "Easy",
        "topic": "Math / Strings",
        "description": "Given integer n, return a list of strings 1..n:\n'Fizz' for multiples of 3, 'Buzz' for 5, 'FizzBuzz' for both.",
        "examples": [
            "Input: n=3  →  ['1','2','Fizz']",
            "Input: n=5  →  ['1','2','Fizz','4','Buzz']",
        ],
        "fn_name": "fizz_buzz",
        "params": "n: int",
        "approach": "Iterate 1..n. Check divisibility by 15 first, then 3, then 5.",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
        "solution": """\
    res = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            res.append('FizzBuzz')
        elif i % 3 == 0:
            res.append('Fizz')
        elif i % 5 == 0:
            res.append('Buzz')
        else:
            res.append(str(i))
    return res""",
        "test_cases": [
            "fizz_buzz(3) == ['1','2','Fizz']",
            "fizz_buzz(5) == ['1','2','Fizz','4','Buzz']",
        ],
    },
    {
        "slug": "linked_list_cycle",
        "title": "Linked List Cycle",
        "difficulty": "Easy",
        "topic": "Linked List / Two Pointers",
        "description": "Given the head of a linked list, determine if it has a cycle.",
        "examples": [
            "3→2→0→-4→(back to 2)  →  True",
            "1→2  →  False",
        ],
        "fn_name": "has_cycle",
        "params": "head",
        "approach": "Floyd's cycle detection: slow pointer moves 1 step,\nfast pointer moves 2 steps. If they meet, cycle exists.",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "solution": """\
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False""",
        "test_cases": [
            "has_cycle(cycle_list) == True",
            "has_cycle([1,2])      == False",
        ],
    },
]


def pick_problem(date_slug: str) -> dict:
    h = int(hashlib.md5(date_slug.encode()).hexdigest(), 16)
    return PROBLEMS[h % len(PROBLEMS)]
