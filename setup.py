from setuptools import setup, find_packages

setup(
    name="doctor_booking_assistant",
    version="0.1.0",
    packages=find_packages(where="app"),
    package_dir={"": "app"},
    install_requires=[
        "streamlit>=1.28.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "numpy>=1.24.0",
        "sounddevice>=0.4.6",
        "scipy>=1.10.0",
        "elevenlabs>=0.2.21",
        "openai>=1.0.0"
    ],
    python_requires=">=3.8",
)
