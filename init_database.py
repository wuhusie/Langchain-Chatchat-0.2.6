import shutup  # 导入 shutup 库用于抑制不必要的警告输出
shutup.please()  # 调用 shutup 的 please 方法来禁用警告

import sys  # 导入系统模块
sys.path.append(".")  # 将当前目录添加到 Python 路径中，使其可以导入当前目录下的模块

# 从 server/knowledge_base/migrate.py 导入数据库操作相关的函数
from server.knowledge_base.migrate import create_tables, reset_tables, folder2db, prune_db_docs, prune_folder_files

from configs.model_config import NLTK_DATA_PATH  # 从配置文件中导入 NLTK 数据路径
import nltk  # 导入自然语言处理工具包
nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path  # 将自定义 NLTK 数据路径添加到默认路径列表前面

from datetime import datetime  # 导入 datetime 用于时间计算
import sys  # 导入 sys 模块用于处理命令行参数


if __name__ == "__main__":  # 确保代码只在直接运行时执行，而不是在被导入时执行
    import argparse  # 导入命令行参数解析模块
    
    # 创建参数解析器对象，设置描述信息
    parser = argparse.ArgumentParser(description="please specify only one operate method once time.")

    # 添加重建向量存储的命令行选项，-r 或 --recreate-vs
    parser.add_argument(
        "-r",
        "--recreate-vs",
        action="store_true",  # 设置为布尔标志，不需要额外参数
        # 重建向量存储
        # 如果您已将文档文件复制到内容文件夹
        # 但向量存储尚未填充或默认向量存储类型/嵌入模型已更改，请使用此选项
        help=('''
            recreate vector store.
            use this option if you have copied document files to the content folder, 
            but vector store has not been populated or DEFAUL_VS_TYPE/EMBEDDING_MODEL changed.
            '''
        )
    )

    # 添加更新数据库中文件的命令行选项，-u 或 --update-in-db
    parser.add_argument(
        "-u",
        "--update-in-db",
        action="store_true",  # 设置为布尔标志
        # 更新数据库中的文件
        # 如果您想为数据库中存在的文件重新创建向量，并跳过仅存在于本地文件夹中的文件，请使用此选项
        help=('''
            update vector store for files exist in database.
            use this option if you want to recreate vectors for files exist in db and skip files exist in local folder only.
            '''
        )
    )

    # 添加增量更新的命令行选项，-i 或 --increament
    
    parser.add_argument(
        "-i",
        "--increament",
        action="store_true",  # 设置为布尔标志
        # 如果您想为本地文件夹中存在而数据库中不存在的文件创建向量，请使用此选项
        help=('''
            update vector store for files exist in local folder and not exist in database.
            use this option if you want to create vectors increamentally.
            '''
               
        )
    )

    # 添加清理数据库的命令行选项
    
    parser.add_argument(
        "--prune-db",
        action="store_true",  # 设置为布尔标志
        # 删除数据库中不存在于本地文件夹的文档
        # 用户在文件浏览器中删除了一些文档文件后使用
        help=('''
            delete docs in database that not existed in local folder.
            it is used to delete database docs after user deleted some doc files in file browser
            '''  
               
        )
    )

    # 添加清理本地文件夹的命令行选项
    parser.add_argument(
        "--prune-folder",
        action="store_true",  # 设置为布尔标志
        # 删除本地文件夹中不存在于数据库的文档文件
        # 用于通过删除未使用的文档文件来释放本地磁盘空间。
        help=('''
            delete doc files in local folder that not existed in database.
            is is used to free local disk space by delete unused doc files.
            '''
               
        )
    )

    # 添加知识库名称的命令行选项
    parser.add_argument(
        "--kb-name",
        type=str,  # 参数类型为字符串
        nargs="+",  # 允许输入多个知识库名称
        default=[],  # 默认为空列表

        # 指定要操作的知识库名称。默认是 KB_ROOT_PATH 中存在的所有文件夹。
        help=("specify knowledge base names to operate on. default is all folders exist in KB_ROOT_PATH.")
    )

    if len(sys.argv) <= 1:  # 如果没有提供任何命令行参数
        parser.print_help()  # 打印帮助信息
    else:
        args = parser.parse_args()  # 解析命令行参数
        start_time = datetime.now()  # 记录开始时间

        create_tables()  # 确保所需的数据库表都已创建
        
        # 根据不同的命令行参数执行对应的操作
        if args.recreate_vs:  # 如果指定了重建向量存储
            reset_tables()  # 重置所有数据库表
            print("database talbes reseted")  # 打印重置完成信息
            print("recreating all vector stores")  # 打印开始重建向量存储的信息
            folder2db(kb_names=args.kb_name, mode="recreate_vs")  # 重新创建向量存储
        elif args.update_in_db:  # 如果指定了更新数据库中的文件
            folder2db(kb_names=args.kb_name, mode="update_in_db")  # 更新数据库中现有文件的向量
        elif args.increament:  # 如果指定了增量更新
            folder2db(kb_names=args.kb_name, mode="increament")  # 执行增量更新
        elif args.prune_db:  # 如果指定了清理数据库
            prune_db_docs(args.kb_name)  # 清理数据库中不存在的文档记录
        elif args.prune_folder:  # 如果指定了清理文件夹
            prune_folder_files(args.kb_name)  # 清理本地文件夹中不存在于数据库的文件

        end_time = datetime.now()  # 记录结束时间
        print(f"总计用时： {end_time-start_time}")  # 打印程序运行的总时间