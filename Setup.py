import sys
try:
    if sys.version_info < (3, 5):
        raise RuntimeError("")
    import PyQt5
except RuntimeError as error:
    print("Application loading error!")
    print("Your Python version is out of date!")
    print()
    print("Required Python version >= 3.5")
    print("Your version: {}.{}.{}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
    print("Download adn install latest Python: https://www.python.org/downloads")
    print()
except ImportError as error:
    print("Application loading error!")
    print("Some modules are missing!")
    print()
    print(error)
    if error.name == "PyQt5":
        print("Download and install PyQT5: https://www.riverbankcomputing.com/software/pyqt/download5")
    print()
    print("Please install all required modules!")
else:
    print("Application ready to use!")
    print("Run DATComposer.pyw or DATComposer.py for start working!")

input()
