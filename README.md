# Unofficial Python Installer for Windows

This repository provides an unofficial Python installer specifically for Windows environments. Unlike the official installer, this custom installer is tailored to meet specific requirements and offer additional configuration options.

## Features

* **Windows Support**: Optimized for Python installation on Windows systems.
* **Unofficial**: Offers additional options and configurations not available in the official Python installer.
* **Python Installer**: Simplifies the Python installation process, reducing the need for manual setup.

## Installation Guide

1. **Download the Latest Release**
   Go to the [releases page](https://github.com/) and download the latest `.zip` file of the application.

2. **Extract the ZIP Archive**
   Extract the contents of the ZIP file to your desired installation directory. For example, you might choose `C:\my-python-installer`.

3. **Run the Installer**
   Inside the extracted directory, execute the installer (typically `installer.py` or similar) to begin the installation process.

   ```bash
   python installer.py
   ```

   This will install Python to the `installation_directory/python` folder.

4. **Verify Installation**
   After installation is complete, verify that Python is installed correctly by opening a command prompt and running the following command:

   ```bash
   installation_directory\python\python --version
   ```

   If Python is installed successfully, you should see the Python version displayed.

## Notes

* The installer does not create any symbolic links, so you will need to manually add Python to your system's PATH environment variable if desired.
* This installation method does not automatically link Python to the system's global environment. You will need to refer to the installation directory when running Python unless you manually adjust your PATH.

## License

This project is licensed under the [GNU General Public License v3.0 (GPL-3.0)](LICENSE).
