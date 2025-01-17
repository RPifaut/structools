import os
import pytest

def run_tests():

    curr_path = os.path.dirname(__file__)
    test_dir = os.path.abspath(os.path.join(curr_path, os.pardir, os.pardir))
    exit_code = pytest.main([test_dir])

    return exit_code

# if __name__ == "__main__":

#     cur_path = os.path.dirname(__file__)
#     test_path = os.path.abspath(os.path.join(cur_path, os.pardir, os.pardir))
#     print(test_path)