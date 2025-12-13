from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sftp-sync",
    version="1.0.0",
    author="perfectbullet",
    description="同步本地代码到远程服务器的工具 (SFTP Sync Tool)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/perfectbullet/sftp_sync",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sftp-sync=sftp_sync.cli:main",
            "sftp-sync-web=sftp_sync.web_server:main",
        ],
    },
)
