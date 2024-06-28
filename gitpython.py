import os
import subprocess
from git import Repo
import win32cred
import sys

# Git仓库的路径
repo_path = r'C:\Users\dtyangchi\UnicomResp\sk2-mobile'

# 初始化Git仓库对象
repo = Repo(repo_path)

# 提交信息列表
commit_messages = [
    {
        'author_name': 'Author1',
        'author_email': 'author1@example.com',
        'username': 'jc-caoshuo',
        'password': '9#vKlT6p811',
        'commit_messages': '提交描述1'
    },
    {
        'author_name': 'Author2',
        'author_email': 'author2@example.com',
        'username': 'jc-zhangsheng',
        'password': 'ChuDian@2024',
        'commit_messages': '提交描述2'
    }
    # 可以继续添加更多提交信息
]

def get_changed_files(repo):
    # 获取已追踪且变更的文件
    changed_files = [item.a_path for item in repo.index.diff(None)]
    # 获取未追踪的文件，并将其与已变更的文件列表合并
    changed_files.extend(repo.untracked_files)
    return changed_files

def count_lines_in_files(files, repo_path):
    total_lines = 0
    for file in files:
        file_path = os.path.join(repo_path, file)
        if os.path.isfile(file_path):  # 确保文件存在
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                total_lines += len(f.readlines()) 
    return total_lines

def count_lines_in_file(file_path):
    if os.path.isfile(file_path):  # 确保文件存在
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    return 0

def set_windows_credentials(target, username, password):
    """
    Save credentials to Windows Credential Store.
    """
    credential = dict(
        Type=win32cred.CRED_TYPE_GENERIC,
        TargetName=target,
        UserName=username,
        CredentialBlob=password,
        Persist=win32cred.CRED_PERSIST_LOCAL_MACHINE
    )

    try:
        win32cred.CredWrite(credential, 0)
        print(f"Credential saved successfully for {target}.")
    except Exception as e:
        print(f"Failed to save credential: {str(e)}", file=sys.stderr)

def add_and_commit_files(author_name, author_email, commit_message, file_list, repo):
    # 配置git用户信息
    repo.config_writer().set_value("user", "name", author_name).release()
    repo.config_writer().set_value("user", "email", author_email).release()
    
    if not file_list:
        print("No changes to commit.")
        return 
    
    # 添加变更文件
    repo.index.add(file_list)
    
    # 提交代码
    repo.index.commit(commit_message)
    print(f"Committed {len(file_list)} files by {author_name} with message: '{commit_message}'")
    
    # 推送到远程仓库
    #origin = repo.remote(name='origin')
    #origin.push(refspec='dev:dev')
    print(f"Pushed changes to remote repository 'dev' branch. {author_name}")

# 确保我们在目标分支上
branch_name = 'dev'
if branch_name not in repo.heads:
    repo.create_head(branch_name)
repo.heads[branch_name].checkout()
# 全局变量，用于统计所有提交的代码行数
total_committed_lines = 0
# 获取当前变更的所有文件
changed_files = get_changed_files(repo)
# 按行数分配文件给每一个提交者
for commit_info in commit_messages:
    username = commit_info['username']
    password = commit_info['password']
    repo_url = 'http://172.24.128.158:8080/tfs/NetDataCollection/DPI%E6%95%B0%E6%8D%AE%E5%AE%9E%E6%97%B6%E7%9B%91%E6%8E%A7%E7%B3%BB%E7%BB%9F/_git/sk2-mobiles'

    # 设置远程仓库URL而不包含用户名
    repo.remotes.origin.set_url(repo_url)
    
    # 替换凭据
    set_windows_credentials("git:http://172.24.128.158:8080", username, password)
    
    total_lines = 0
    files_to_commit = []
    
    # 累加文件直到达到750行
    while changed_files and total_lines < 750:
        file = changed_files.pop(0)
        file_path = os.path.join(repo_path, file)
        lines = count_lines_in_file(file_path)
        total_lines += lines
        files_to_commit.append(file)
        
    # 提交文件并立即推送
    if files_to_commit:
        add_and_commit_files(commit_info['author_name'], commit_info['author_email'], commit_info['commit_messages'], files_to_commit, repo)
        total_committed_lines += total_lines
        print(f"Total lines: {total_lines}")
    else:
        print(f"Not enough lines to commit for {username}. Total lines: {total_lines}")
# 打印所有提交的总行数
print(f"Total committed lines: {total_committed_lines}")
