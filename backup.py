# 查找两个指定目录下有哪些文件发生了变化，用于备份
# 用文件大小和文件修改时间比对，可能存在偏差
# 备份时会删除备份文件夹的文件！请谨慎操作
# 环境：Python3
import os
import shutil

args_dir_input = r'C:\King'              # 实际目录
args_dir_input_backup = r'D:\King备份'    # 备份目录
args_backup = True    # 用于指示仅仅查找还是进行自动备份
args_level = 0        # 0-比较时间和大小
                      # 1-比较大小

def size_format(size):
    """把size从Int形式格式化为KB形式"""
    size_layer = 0
    while True:
        if size >= 1024:
            size_layer += 1
            size /= 1024
        else:
            break
    return "{:.2f}{}".format(size, ["Byte", "KB", "MB", "GB", "TB"][size_layer])


class Backup(object):
    def __init__(self, flag_backup, flag_level, dir_input, dir_input_backup):
        self.flag_backup = flag_backup
        self.flag_level = flag_level
        self.dir_input = dir_input
        self.dir_input_backup = dir_input_backup


    def get_size_mtime(self, path):
        # 获取文件夹/文件大小和最新更改时间
        # 获取文件夹/文件大小
        if os.path.isdir(path):   # 文件夹
            mtime = size = 0
            for root, dirs, files in os.walk(path):
                for file in files:
                    fullpath = os.path.join(root, file)
                    size += os.path.getsize(fullpath)
                    mtime = max(os.stat(fullpath).st_mtime, mtime)
        else:        # 文件
            size = os.path.getsize(path)
            mtime = os.stat(path).st_mtime
        if self.flag_level == 0:
            return size, mtime
        elif self.flag_level == 1:
            return size, 0    # 多返回一个0方便获取文件大小用于展示


    def checkdir(self, dir_now, dir_bak, layer):
        # 比较文件夹
        filelist_now = os.listdir(dir_now)  # dir_now = 待比对实际路径文件夹
        filelist_bak = os.listdir(dir_bak)  # dir_bak = 待比对备份路径文件夹
        for file in filelist_now:  # file=文件/文件夹名
            path_now = os.path.join(dir_now, file)  # 实际路径下文件/文件夹名
            path_bak = os.path.join(dir_bak, file)  # 备份路径下文件/文件夹名
            if file not in filelist_bak:  # 实际路径下存在，备份路径下不存在
                print("{}【+】新增文件/文件夹：{}-----{}".format("      " * layer, path_now, size_format(self.get_size_mtime(path_now)[0])))
                if self.flag_backup:  # 如果需要备份
                    if os.path.isdir(path_now):
                        shutil.copytree(path_now, path_bak)     # 复制文件夹
                    else:
                        shutil.copy(path_now, path_bak)          # 复制文件
            else:  # 两者的同名文件/文件夹
                if os.path.isdir(path_now):  # 文件夹
                    smnow = self.get_size_mtime(path_now)
                    if smnow != self.get_size_mtime(path_bak):
                        print("{}【*】文件夹存在变化：{}-----{}".format("      " * layer, path_now, size_format(smnow[0])))
                        self.checkdir(path_now, path_bak, layer + 1)  # 递归
                else:  # 文件
                    smnow = self.get_size_mtime(path_now)
                    if smnow != self.get_size_mtime(path_bak):
                        print("{}【*】文件存在变化：{}-----{}".format("      " * layer, path_now, size_format(smnow[0])))
                        if self.flag_backup:
                            shutil.copy(path_now, path_bak)     #　复制文件覆盖
        for file in filelist_bak:
            if file not in filelist_now:
                path_bak = os.path.join(dir_bak, file)
                print("{}【-】减少文件/文件夹：{}-----{}".format("      " * layer, path_bak, size_format(self.get_size_mtime(path_bak)[0])))
                if self.flag_backup:
                    if os.path.isdir(path_bak):
                        shutil.rmtree(path_bak)        # 删除文件夹
                    else:
                        os.unlink(path_bak)            # 删除文件

    def start(self):
        print("【#】开始比对")
        if self.get_size_mtime(self.dir_input) == self.get_size_mtime(self.dir_input_backup):
            print("【#】无变化，无需更新备份")
            return
        self.checkdir(self.dir_input, self.dir_input_backup, 0)


if __name__ == '__main__':
    Backup(args_backup, args_level, args_dir_input, args_dir_input_backup).start()
