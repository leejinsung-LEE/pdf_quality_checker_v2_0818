# setup.py
"""
PDF Quality Checker v2.0 설치 스크립트
"""

from setuptools import setup, find_packages
from pathlib import Path

# README 읽기
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()

# requirements.txt 읽기
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="pdf-quality-checker",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="인쇄용 PDF 파일의 품질을 자동으로 검사하는 도구",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pdf_quality_checker_v2",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/pdf_quality_checker_v2/issues",
        "Documentation": "https://github.com/yourusername/pdf_quality_checker_v2/wiki",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Printing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=find_packages(include=["src", "src.*"]),
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "gui": [
            "customtkinter>=5.2.0",
            "tkinterdnd2>=0.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdf-quality-checker=main:main",
            "pdfqc=main:main",  # 짧은 별칭
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json"],
    },
    zip_safe=False,
    keywords="pdf quality checker print prepress preflight",
)