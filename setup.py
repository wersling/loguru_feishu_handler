from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="loguru-feishu-handler",
    version="2.0.3",
    author="seanzou",
    author_email="wersling@gmail.com",
    description="Loguru 飞书消息推送 Handler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wersling/loguru_feishu_handler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "loguru>=0.6.0",
        "requests>=2.20.0",
    ],
    keywords="loguru feishu logging handler webhook",
    project_urls={
        "Bug Reports": "https://github.com/wersling/loguru_feishu_handler/issues",
        "Source": "https://github.com/wersling/loguru_feishu_handler",
    },
) 