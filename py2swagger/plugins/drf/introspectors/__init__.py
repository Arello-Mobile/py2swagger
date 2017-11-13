from distutils.version import StrictVersion
from rest_framework import VERSION as REST_FRAMEWORK_VERSION

REST_FRAMEWORK_V3 = StrictVersion(REST_FRAMEWORK_VERSION) > StrictVersion('3.0.0')
