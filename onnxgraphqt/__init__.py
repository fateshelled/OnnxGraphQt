import os, sys
import PySide2

plugin_path = os.path.join(os.path.dirname(PySide2.__file__),
                           "Qt", "plugins", "platforms")
os.environ["QT_PLUGIN_PATH"] = plugin_path
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
