"""
Build the .saver bundle:
    cd screensaver
    python setup.py py2app
"""

from setuptools import setup

plist = {
    "NSPrincipalClass": "ThreeBodySaver",
}

setup(
    plugin=["three_body_saver.py"],
    data_files=[("", ["config.toml"])],
    options={
        "py2app": {
            "extension": ".saver",
            "plist": plist,
        },
    },
    setup_requires=[
        "py2app",
        "pyobjc-framework-Cocoa",
        "pyobjc-framework-ScreenSaver",
    ],
)
