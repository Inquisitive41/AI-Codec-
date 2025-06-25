from setuptools import setup, find_packages

setup(
    name="aicodec",
    version="0.1.0",
    description="Сверхэффективный алгоритм контекстно-зависимого сжатия структурированных данных",
    author="Qalam AGI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
    ],
    python_requires=">=3.7",
    license="MIT",
)
