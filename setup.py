from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="berkeley-lab-email-analyzer",
    version="1.0.0",
    author="Berkeley Lab Email Analyzer Team",
    author_email="your-email@lbl.gov",
    description="Analyze Gmail emails for Berkeley Lab record classification using local LLM via Ollama",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/berkeley-lab-email-analyzer",
    
    # Package configuration
    packages=find_packages(),
    include_package_data=True,
    
    # Dependencies
    install_requires=read_requirements() or [
        "google-auth>=2.23.4",
        "google-auth-oauthlib>=1.1.0",
        "google-auth-httplib2>=0.1.1",
        "google-api-python-client>=2.108.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
    ],
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    
    # Entry points for command-line scripts
    entry_points={
        'console_scripts': [
            'email-analyzer=email_analyzer.cli:main',
        ],
    },
    
    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Communications :: Email",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Keywords for PyPI search
    keywords=[
        "email", "analysis", "gmail", "llm", "ollama", "berkeley-lab", 
        "records", "classification", "automation"
    ],
    
    # Package data
    package_data={
        'email_analyzer': [
            'templates/*.txt',
            'config/*.yaml',
        ],
    },
    
    # Data files
    data_files=[
        ('config', ['config/default.env']),
    ],
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/your-org/berkeley-lab-email-analyzer/issues",
        "Source": "https://github.com/your-org/berkeley-lab-email-analyzer",
        "Documentation": "https://berkeley-lab-email-analyzer.readthedocs.io/",
    },
    
    # Zip safe
    zip_safe=False,
)
