import logging
import os
import warnings
from typing import Any

import jpype
import scyjava
import scyjava.config

MAVEN_COORDINATE = "ome:formats-gpl:RELEASE"

# Check if the BIOFORMATS_VERSION environment variable is set
# and if so, use it as the Maven coordinate
if (coord := os.getenv("BIOFORMATS_VERSION", None)) is not None:
    # allow a single version number to be passed
    if ":" not in coord and all(x.isdigit() for x in coord.split(".")):
        # if the coordinate is just a version number, use the default group and artifact
        coord = f"ome:formats-gpl:{coord}"

    # ensure the coordinate is valid
    if 2 > len(coord.split(":")) > 5:
        warnings.warn(
            f"Invalid BIOFORMATS_VERSION env var: {coord!r}. "
            "Must be a valid maven coordinate with 2-5 elements. "
            f"Using default {MAVEN_COORDINATE!r}",
            stacklevel=2,
        )
    else:
        MAVEN_COORDINATE = coord

scyjava.config.endpoints.append(MAVEN_COORDINATE)
scyjava.config.endpoints.append("ch.qos.logback:logback-classic")

# #################################### LOGGING ####################################

# python-side logger

LOGGER = logging.getLogger("bffile")
fmt = (
    "%(asctime)s.%(msecs)03d "  # timestamp with milliseconds
    "[%(levelname)-5s] "  # level, padded
    "%(name)s:%(lineno)d - "  # logger name and line no.
    "%(message)s"  # the log message
)
datefmt = "%Y-%m-%d %H:%M:%S"
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
# avoid double-logs if somebody has already attached handlers
if not any(isinstance(h, logging.StreamHandler) for h in LOGGER.handlers):
    LOGGER.addHandler(handler)

_LOGGING_REDIRECTED = False


def redirect_java_logging(logger: logging.Logger | None = None) -> None:
    """Redirect Java logging to Python logger."""
    global _LOGGING_REDIRECTED
    if _LOGGING_REDIRECTED:
        return

    scyjava.start_jvm()

    _logger = logger or LOGGER

    class PyAppender:
        def doAppend(self, event: Any) -> None:
            # event is an ILoggingEvent
            msg = str(event.getFormattedMessage())
            level = str(event.getLevel())
            # dispatch to Python logger
            getattr(logger, level.lower(), _logger.info)(msg)

    # Create a proxy for the Appender interface
    proxy = jpype.JProxy("ch.qos.logback.core.Appender", inst=PyAppender())

    # Get the LoggerContext
    Slf4jFactory = scyjava.jimport("org.slf4j.LoggerFactory")
    root = Slf4jFactory.getILoggerFactory().getLogger("ROOT")

    # remove the console appender
    for appender in root.iteratorForAppenders():
        if appender.getName() == "console":
            root.detachAppender(appender)
            break

    # add the Python appender
    root.addAppender(proxy)
    _LOGGING_REDIRECTED = True
