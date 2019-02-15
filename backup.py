# 查找两个指定目录下有哪些文件发生了变化，用于备份
# 用文件大小和文件修改时间比对，可能存在偏差
# 备份时会删除备份文件夹的文件！请谨慎操作
# 环境：Python3
import os
import shutil

# 一些配置变量
dir_input = r''              # 实际目录
dir_input_backup = r''       # 备份目录
flag_backup = False          # 用于指示仅仅查找还是进行备份，默认情况下为仅仅查找
#flag_backup = True


def get_dir_size_mtime(path_dir):
    '''获取文件夹大小和最新更改时间'''
    mtime = size = 0
    for root, dirs, files in os.walk(path_dir):
        for file in files:
            fullpath = os.path.join(root, file)
            size += os.path.getsize(fullpath)
            mtime = max(os.stat(fullpath).st_mtime, mtime)
    return size, mtime


def get_file_size_mtime(path_file):
    '''获取文件大小和最新更改时间'''
    size = os.path.getsize(path_file)
    mtime = os.stat(path_file).st_mtime
    return size, mtime


def checkdir(dir_now, dir_bak, layer):
    '''比较文件夹'''
    filelist_now = os.listdir(dir_now)  # dir_now = 待比对实际路径文件夹
    filelist_bak = os.listdir(dir_bak)  # dir_bak = 待比对备份路径文件夹
    for file in filelist_now:    # file=文件/文件夹名
        path_now = os.path.join(dir_now, file)   # 实际路径下文件/文件夹名
        path_bak = os.path.join(dir_bak, file)   # 备份路径下文件/文件夹名
        if file not in filelist_bak:             # 实际路径下存在，备份路径下不存在
            print("{}【+】新增文件/文件夹：{}".format("      " * layer, path_now))
            if flag_backup:  # 如果需要备份
                if os.path.isdir(path_now):   # 文件夹
                    shutil.copytree(path_now, path_bak)
                else:      # 文件
                    shutil.copy(path_now, path_bak)
        else:                    # 两者的同名文件/文件夹
            if os.path.isdir(path_now):   # 文件夹
                if get_dir_size_mtime(path_now) != get_dir_size_mtime(path_bak):
                    print("{}【*】文件夹存在变化：{}".format("      " * layer, path_now))
                    checkdir(path_now, path_bak, layer+1)   # 递归
            else:                    # 文件
                if get_file_size_mtime(path_now) != get_file_size_mtime(path_bak):
                    print("{}【*】文件存在变化：{}".format("      " * layer, path_now))
                    if flag_backup:
                        shutil.copy(path_now, path_bak)
    for file in filelist_bak:
        if file not in filelist_now:
            path_bak = os.path.join(dir_bak, file)
            print("{}【-】减少文件/文件夹：{}".format("      " * layer, path_bak))
            if flag_backup:
                if os.path.isdir(path_bak):
                    shutil.rmtree(path_bak)
                else:
                    os.unlink(path_bak)


def main():
    '''主函数'''
    print("【#】开始比对")
    if get_dir_size_mtime(dir_input) == get_dir_size_mtime(dir_input_backup):
        print("【#】无变化，无需更新备份")
        return
    checkdir(dir_input, dir_input_backup, 0)


if __name__ == '__main__':
    main()
