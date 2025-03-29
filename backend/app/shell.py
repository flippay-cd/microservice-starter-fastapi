"""
Interactive shell for FastAPI based on IPython
- Access to application object via `app` variable
- Access to di container via `di` variable
- Support for asynchronous functions
"""
import logging
import sys
from pathlib import Path

from IPython.terminal.embed import InteractiveShellEmbed
from traitlets.config import Config

sys.path.append(str(Path(__file__).resolve().parent))
from main import app

logging.getLogger("asyncio").setLevel(logging.WARNING)  # Disable unnecessary logging

# Configuring IPython to Support await and asyncio
cfg = Config()
cfg.InteractiveShellEmbed.autoawait = True
cfg.InteractiveShellEmbed.loop_runner = "asyncio"

# Add a custom namespace with accessible variables app and di
InteractiveShellEmbed(config=cfg, banner1=__doc__, user_ns={"app": app, "di": app.container})()
