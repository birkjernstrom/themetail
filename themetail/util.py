# -*- coding: utf-8 -*-

import os
import sys
import logging
import subprocess

logger = logging.getLogger('themetail')
logger.setLevel(logging.DEBUG)
logging_handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(message)s')
logging_handler.setFormatter(formatter)
logger.addHandler(logging_handler)


def execute_hook(name, *params):
    hook = os.path.join(os.getcwd(), 'hooks/%s' % name)
    if not os.path.isfile(hook):
        return True

    if not os.access(hook, os.X_OK):
        msg = 'Cannot run hook "%s" because it is not executable.'
        logging.error(msg, name)
        sys.exit(1)

    params.insert(0, hook)
    return not subprocess.call(hook)
