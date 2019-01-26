import os

path_in='E:\\1111'
files=os.listdir(path_in)
path_out='E:\\file'
for i in files:
    path=path_in+'\\'+ '"'+ i + '"'
    # print(path)
    command = r'C:\"Program Files"\WinRAR\WinRAR.exe x ' + path +' '+ path_out
    # print(command)
    os.system(command)
print('此文件夹已解压完')



