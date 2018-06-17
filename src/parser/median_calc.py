import random


def _partition(input_list, random_val):
    smaller = []
    bigger = []
    for val in input_list:
        if val < random_val:
            smaller += [val]
        if val > random_val:
            bigger += [val]
    return smaller, [random_val], bigger


def _top_k(input_list, k):
    random_val = input_list[random.randrange(len(input_list))]
    (left, middle, right) = _partition(input_list, random_val)
    if len(left) == k:
        return left
    if len(left)+1 == k:
        return left + middle
    if len(left) > k:
        return _top_k(left, k)
    return left + middle + _top_k(right, k - len(left) - len(middle))


def median(input_list):
    """
    This is a special case of a selection algorithm that can find the kth
    smallest element of an array with k is the half of the size of the array.
    Complexity is O(n)
    Original source: https://stackoverflow.com/a/22752040
    """
    n = len(input_list)
    if n == 1:
        return input_list[0]
    k = _top_k(input_list, n / 2 + 1)
    return max(k)
