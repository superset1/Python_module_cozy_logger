# Python module Gitlab Parser

## Installation

```bash
pip install cozy_logger
```

## Usage

```
from cozy_logger import Logger

Logger = Logger()
logger = Logger.get_logger()
if Logger.LOG_FILE:
    print(f"See log here: {Logger.LOG_FILE}")
```
