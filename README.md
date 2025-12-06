# SFTP Sync

同步本地代码到远程服务器的工具 / A tool for synchronizing local code to remote servers via SFTP

[English](#english) | [中文](#中文)

---

## English

### Features

- **Flexible Authentication**: Support for both password and SSH key authentication (RSA, DSA, ECDSA, Ed25519)
- **Pattern-based Filtering**: Include/exclude files using glob patterns (like .gitignore)
- **Incremental Sync**: Only uploads changed files (compares modification time and size)
- **Dry Run Mode**: Preview changes before executing
- **Progress Tracking**: Real-time progress bars for file transfers
- **Delete Synchronization**: Optionally delete remote files that don't exist locally
- **Backup Support**: Backup remote files before overwriting
- **Permission Preservation**: Maintain file permissions during sync
- **Configuration Files**: Use YAML config files for repeated syncs
- **Comprehensive Logging**: Detailed operation logs with verbose mode
- **Error Handling**: Robust error handling and recovery
- **Security Features**: Host key verification, symlink protection, circular reference detection

### Installation

#### From Source

```bash
git clone https://github.com/perfectbullet/sftp_sync.git
cd sftp_sync
pip install -r requirements.txt
pip install -e .
```

#### Using pip

```bash
pip install -e git+https://github.com/perfectbullet/sftp_sync.git#egg=sftp-sync
```

### Quick Start

#### Basic Usage with Password

```bash
sftp-sync --host 192.168.1.100 --username myuser --password mypass \
          --local-dir ./my-project --remote-dir /var/www/html
```

#### Using SSH Key (Recommended)

```bash
sftp-sync --host example.com --username myuser \
          --private-key ~/.ssh/id_rsa \
          --local-dir ./my-project --remote-dir /var/www/html
```

#### Using Configuration File

```bash
sftp-sync --config config.yaml
```

### Configuration File

Create a `config.yaml` file (see [examples/config.yaml](examples/config.yaml) for a complete example):

```yaml
# Connection settings
host: "192.168.1.100"
port: 22
username: "myuser"
password: "mypassword"  # Or use private_key

# Directories
local_dir: "./my-project"
remote_dir: "/var/www/html"

# Exclude patterns
exclude_patterns:
  - "*.pyc"
  - "__pycache__"
  - ".git"
  - "node_modules"
  - ".env"

# Options
delete_remote: false
preserve_permissions: true
dry_run: false
verbose: false
```

### Command-Line Options

```
Connection Options:
  --host HOST               Remote host (IP or hostname)
  --port PORT               SSH port (default: 22)
  --username USERNAME       SSH username
  --password PASSWORD       SSH password
  --private-key PATH        Path to SSH private key
  --private-key-password    Password for encrypted private key

Directory Options:
  --local-dir PATH          Local directory to sync (default: current directory)
  --remote-dir PATH         Remote directory path

Filter Options:
  --include PATTERN         Include pattern (e.g., '*.py')
  --exclude PATTERN         Exclude pattern (e.g., '*.pyc', '__pycache__')

Behavior Options:
  --delete                  Delete remote files not in local
  --no-preserve-permissions Don't preserve file permissions
  --dry-run                 Preview changes without executing
  --verbose, -v             Enable verbose output
  --follow-symlinks         Follow symbolic links
  --backup                  Backup remote files before overwriting

Other Options:
  --config, -c FILE         Use YAML configuration file
  --help, -h                Show help message
```

### Usage Examples

#### Exclude Multiple Patterns

```bash
sftp-sync --host example.com --username user --password pass \
          --local-dir . --remote-dir /app \
          --exclude "*.pyc" --exclude "__pycache__" \
          --exclude ".git" --exclude "node_modules"
```

#### Dry Run (Preview Changes)

```bash
sftp-sync --host example.com --username user --password pass \
          --local-dir ./src --remote-dir /var/www/html \
          --dry-run --verbose
```

#### Sync with Deletion

```bash
sftp-sync --host example.com --username user --private-key ~/.ssh/id_rsa \
          --local-dir ./dist --remote-dir /var/www/html \
          --delete
```

#### Include Only Specific Files

```bash
sftp-sync --host example.com --username user --password pass \
          --local-dir . --remote-dir /app \
          --include "*.py" --include "*.txt"
```

### Use as Python Library

```python
from sftp_sync import SFTPSyncer, Config

# Create configuration
config = Config({
    "host": "192.168.1.100",
    "username": "myuser",
    "password": "mypass",
    "local_dir": "./my-project",
    "remote_dir": "/var/www/html",
    "exclude_patterns": ["*.pyc", "__pycache__", ".git"],
    "dry_run": False,
    "verbose": True
})

# Validate configuration
errors = config.validate()
if errors:
    for error in errors:
        print(f"Error: {error}")
    exit(1)

# Perform synchronization
syncer = SFTPSyncer(config)
syncer.sync()
```

### Pattern Matching

The tool supports glob-style patterns for include/exclude:

- `*` - Matches any characters
- `?` - Matches single character
- `**` - Matches any directory depth
- `*.py` - All Python files
- `test_*.py` - All test files starting with "test_"
- `__pycache__` - Specific directory name
- `*.pyc` - All Python bytecode files
- `.git` - Git directory

Exclude patterns take precedence over include patterns.

### Security Recommendations

1. **Use SSH Keys**: Prefer SSH key authentication over passwords for better security
2. **Host Key Verification**: 
   - By default, host key verification uses `WarningPolicy` (secure mode)
   - Add trusted hosts to `~/.ssh/known_hosts` before first connection
   - Only use `--auto-add-host-key` or `auto_add_host_key: true` for testing/development
   - For production, manually verify and add host keys using: `ssh-keyscan -H <host> >> ~/.ssh/known_hosts`
3. **Protect Config Files**: 
   - Don't commit config files with passwords to version control
   - Add `config.yaml` to `.gitignore`
   - Use file permissions: `chmod 600 config.yaml`
4. **Use Environment Variables**: Store sensitive data in environment variables instead of config files
5. **Restrict Key Permissions**: Set appropriate file permissions for SSH keys: `chmod 600 ~/.ssh/id_rsa`
6. **Symlink Safety**: 
   - Avoid using `--follow-symlinks` unless necessary
   - Tool automatically detects circular symlinks and prevents infinite loops
   - Symlinks pointing outside local directory are skipped for security
7. **Test with Dry Run**: Always test with `--dry-run` first to preview changes
8. **Review Exclude Patterns**: Ensure sensitive files (.env, credentials, keys) are excluded
9. **Backup Important Data**: Use `--backup` flag when overwriting critical files

### Security Features

- **Host Key Verification**: Loads system and user known_hosts files for verification
- **Symlink Protection**: Detects circular references and prevents directory traversal attacks
- **Credential Protection**: Passwords are masked in logs and output
- **SSH Key Support**: Supports all modern key types (RSA, DSA, ECDSA, Ed25519)
- **Path Validation**: Validates that symlinks don't escape the local directory boundary

### Troubleshooting

**Connection Failed**
- Check host, username, and credentials
- Verify firewall and network settings
- Ensure SSH service is running on remote host
- If you get "Host key verification failed":
  - Add the host to known_hosts: `ssh-keyscan -H <host> >> ~/.ssh/known_hosts`
  - Or use `--auto-add-host-key` flag for testing (not recommended for production)

**Permission Denied**
- Check SSH key permissions (should be 600): `chmod 600 ~/.ssh/id_rsa`
- Verify username has access to remote directory
- Check remote directory permissions
- Ensure SSH key is added to remote server's authorized_keys

**Files Not Syncing**
- Check exclude patterns
- Use `--verbose` to see which files are being processed
- Use `--dry-run` to preview what would be synced

---

## 中文

### 功能特性

- **灵活的认证方式**: 支持密码和SSH密钥认证（RSA、DSA、ECDSA、Ed25519）
- **基于模式的过滤**: 使用glob模式包含/排除文件（类似.gitignore）
- **增量同步**: 仅上传更改的文件（比较修改时间和大小）
- **预演模式**: 执行前预览更改
- **进度跟踪**: 文件传输的实时进度条
- **删除同步**: 可选择删除远程不存在于本地的文件
- **备份支持**: 覆盖前备份远程文件
- **权限保持**: 同步期间保持文件权限
- **配置文件**: 使用YAML配置文件进行重复同步
- **详细日志**: 带详细模式的详细操作日志
- **错误处理**: 强大的错误处理和恢复机制
- **安全特性**: 主机密钥验证、符号链接保护、循环引用检测

### 安装

#### 从源码安装

```bash
git clone https://github.com/perfectbullet/sftp_sync.git
cd sftp_sync
pip install -r requirements.txt
pip install -e .
```

#### 使用pip安装

```bash
pip install -e git+https://github.com/perfectbullet/sftp_sync.git#egg=sftp-sync
```

### 快速开始

#### 使用密码的基本用法

```bash
sftp-sync --host 192.168.1.100 --username myuser --password mypass \
          --local-dir ./my-project --remote-dir /var/www/html
```

#### 使用SSH密钥（推荐）

```bash
sftp-sync --host example.com --username myuser \
          --private-key ~/.ssh/id_rsa \
          --local-dir ./my-project --remote-dir /var/www/html
```

#### 使用配置文件

```bash
sftp-sync --config config.yaml
```

### 配置文件

创建一个 `config.yaml` 文件（完整示例见 [examples/config.yaml](examples/config.yaml)）：

```yaml
# 连接设置
host: "192.168.1.100"
port: 22
username: "myuser"
password: "mypassword"  # 或使用 private_key

# 目录
local_dir: "./my-project"
remote_dir: "/var/www/html"

# 排除模式
exclude_patterns:
  - "*.pyc"
  - "__pycache__"
  - ".git"
  - "node_modules"
  - ".env"

# 选项
delete_remote: false
preserve_permissions: true
dry_run: false
verbose: false
```

### 命令行选项

```
连接选项：
  --host HOST               远程主机（IP或主机名）
  --port PORT               SSH端口（默认：22）
  --username USERNAME       SSH用户名
  --password PASSWORD       SSH密码
  --private-key PATH        SSH私钥路径
  --private-key-password    加密私钥的密码

目录选项：
  --local-dir PATH          要同步的本地目录（默认：当前目录）
  --remote-dir PATH         远程目录路径

过滤选项：
  --include PATTERN         包含模式（例如：'*.py'）
  --exclude PATTERN         排除模式（例如：'*.pyc', '__pycache__'）

行为选项：
  --delete                  删除远程不存在于本地的文件
  --no-preserve-permissions 不保持文件权限
  --dry-run                 预览更改而不执行
  --verbose, -v             启用详细输出
  --follow-symlinks         跟随符号链接
  --backup                  覆盖前备份远程文件

其他选项：
  --config, -c FILE         使用YAML配置文件
  --help, -h                显示帮助信息
```

### 使用示例

#### 排除多个模式

```bash
sftp-sync --host example.com --username user --password pass \
          --local-dir . --remote-dir /app \
          --exclude "*.pyc" --exclude "__pycache__" \
          --exclude ".git" --exclude "node_modules"
```

#### 预演模式（预览更改）

```bash
sftp-sync --host example.com --username user --password pass \
          --local-dir ./src --remote-dir /var/www/html \
          --dry-run --verbose
```

#### 删除同步

```bash
sftp-sync --host example.com --username user --private-key ~/.ssh/id_rsa \
          --local-dir ./dist --remote-dir /var/www/html \
          --delete
```

#### 仅包含特定文件

```bash
sftp-sync --host example.com --username user --password pass \
          --local-dir . --remote-dir /app \
          --include "*.py" --include "*.txt"
```

### 作为Python库使用

```python
from sftp_sync import SFTPSyncer, Config

# 创建配置
config = Config({
    "host": "192.168.1.100",
    "username": "myuser",
    "password": "mypass",
    "local_dir": "./my-project",
    "remote_dir": "/var/www/html",
    "exclude_patterns": ["*.pyc", "__pycache__", ".git"],
    "dry_run": False,
    "verbose": True
})

# 验证配置
errors = config.validate()
if errors:
    for error in errors:
        print(f"错误: {error}")
    exit(1)

# 执行同步
syncer = SFTPSyncer(config)
syncer.sync()
```

### 模式匹配

工具支持glob样式的包含/排除模式：

- `*` - 匹配任何字符
- `?` - 匹配单个字符
- `**` - 匹配任何目录深度
- `*.py` - 所有Python文件
- `test_*.py` - 所有以"test_"开头的测试文件
- `__pycache__` - 特定目录名
- `*.pyc` - 所有Python字节码文件
- `.git` - Git目录

排除模式优先于包含模式。

### 安全建议

1. **使用SSH密钥**: 优先使用SSH密钥认证而不是密码，更加安全
2. **主机密钥验证**: 
   - 默认情况下，主机密钥验证使用 `WarningPolicy`（安全模式）
   - 在首次连接前将受信任的主机添加到 `~/.ssh/known_hosts`
   - 仅在测试/开发环境使用 `--auto-add-host-key` 或 `auto_add_host_key: true`
   - 对于生产环境，手动验证并添加主机密钥：`ssh-keyscan -H <主机> >> ~/.ssh/known_hosts`
3. **保护配置文件**: 
   - 不要将包含密码的配置文件提交到版本控制系统
   - 将 `config.yaml` 添加到 `.gitignore`
   - 设置文件权限：`chmod 600 config.yaml`
4. **使用环境变量**: 将敏感数据存储在环境变量中而不是配置文件
5. **限制密钥权限**: 为SSH密钥设置适当的文件权限：`chmod 600 ~/.ssh/id_rsa`
6. **符号链接安全**: 
   - 除非必要，避免使用 `--follow-symlinks`
   - 工具会自动检测循环符号链接并防止无限循环
   - 指向本地目录外的符号链接会被跳过以确保安全
7. **使用预演测试**: 始终先使用 `--dry-run` 预览更改
8. **检查排除模式**: 确保敏感文件（.env、凭据、密钥）被排除
9. **备份重要数据**: 覆盖关键文件时使用 `--backup` 标志

### 安全特性

- **主机密钥验证**: 加载系统和用户的 known_hosts 文件进行验证
- **符号链接保护**: 检测循环引用并防止目录遍历攻击
- **凭据保护**: 密码在日志和输出中被屏蔽
- **SSH密钥支持**: 支持所有现代密钥类型（RSA、DSA、ECDSA、Ed25519）
- **路径验证**: 验证符号链接不会逃离本地目录边界

### 故障排除

**连接失败**
- 检查主机、用户名和凭据
- 验证防火墙和网络设置
- 确保远程主机上的SSH服务正在运行
- 如果遇到"主机密钥验证失败"错误：
  - 添加主机到 known_hosts：`ssh-keyscan -H <主机> >> ~/.ssh/known_hosts`
  - 或在测试时使用 `--auto-add-host-key` 标志（不建议在生产环境使用）

**权限被拒绝**
- 检查SSH密钥权限（应为600）：`chmod 600 ~/.ssh/id_rsa`
- 验证用户名有访问远程目录的权限
- 检查远程目录权限
- 确保SSH密钥已添加到远程服务器的 authorized_keys

**文件未同步**
- 检查排除模式
- 使用 `--verbose` 查看正在处理哪些文件
- 使用 `--dry-run` 预览将要同步的内容

### 许可证

MIT License

### 贡献

欢迎提交问题和拉取请求！

### 支持

如有问题，请在 [GitHub Issues](https://github.com/perfectbullet/sftp_sync/issues) 上提交。
