import os

# 需求．给我一个文件夹，获取文件夹里面的内容，如果文件夹里面有文件夹也要找出来，还有把文件夹里面面的内容也要找出来


file_name = "/home/python/Desktop"


def _file():



    # 拿到当前文件夹里面所有的内容
    file_list = os.listdir(file_name)

    for i in file_name:

        try:
            # 如果没有抛出异常，就说明这个是文件夹
            os.chdir(i)
            # 添加当前文件夹里面的内容
            file_list.append(os.listdir("./"))

        except:
            # 如果出现了异常就说明就是文件

            continue

    return file_list

if __name__ == '__main__':

    list1 = _file()

    print(list1)





