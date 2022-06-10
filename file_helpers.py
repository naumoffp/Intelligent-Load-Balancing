import csv
import os


# See https://stackoverflow.com/questions/17984809/how-do-i-create-an-incrementing-filename-in-python
def next_path(path_pattern):
    """
    Finds the next free path in an sequentially named list of files

    e.g. path_pattern = 'file-%s.txt':

    file-1.txt
    file-2.txt
    file-3.txt

    Runs in log(n) time where n is the number of existing files in sequence
    """
    i = 1

    # First do an exponential search
    while os.path.exists(path_pattern % i):
        i = i * 2

    # Result lies somewhere in the interval (i/2..i]
    # We call this interval (a..b] and narrow it down until a + 1 = b
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2 # interval midpoint
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

    return path_pattern % b


def write_training_data(path_pattern, headers, data):
    # Example: file-%s.foo
    with open(next_path(path_pattern), 'w+', encoding="UTF8", newline='') as train_file:
        writer = csv.DictWriter(train_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
