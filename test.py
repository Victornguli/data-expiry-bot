import datetime
import os
root_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(root_path, "test.txt")



if __name__ == "__main__":
    with open(os.path.join(root_path, "dskjds.txt"), "a") as fo:
        fo.write("hdshfdghf")
        fo.write("\n")
