import os


file_name = "/home/python/Desktop"
file_list = os.listdir(file_name)
def is_file(name):

    try:
        os.chdir(name)
        return True
    except:
        return False


def _file(file_name):




    for i in file_list:

        temp = is_file(i)

        if temp:
            # 进入到文件夹里面来
            os.chdir(i)

