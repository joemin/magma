"""
Copyright (c) 2016-present, Facebook, Inc.
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

import logging
import re


class EnodebDeviceName():
    """
    This exists only to break a circular dependency. Otherwise there's no
    point of having these names for the devices
    """
    BAICELLS = 'Baicells'
    BAICELLS_OLD = 'Baicells Old'
    BAICELLS_QAFA = 'Baicells QAFA'
    BAICELLS_QAFB = 'Baicells QAFB'
    CAVIUM = 'Cavium'


def get_device_name(
    device_oui: str,
    sw_version: str,
) -> str:
    """
    Use the manufacturer organization unique identifier read during INFORM
    to select the TR data model used for configuration and status reports

    Qualcomm-based Baicells eNodeBs use a TR098-based model different
    from the Intel units. The software version on the Qualcomm models
    also further limits the model usable by that device.

    Args:
        device_oui: string, OUI representing device vendor
        sw_version: string, firmware version of eNodeB device

    Returns:
        DataModel
    """
    if device_oui in {'34ED0B', '48BF74'}:
        if sw_version.startswith('BaiBS_QAFB'):
            return EnodebDeviceName.BAICELLS_QAFB
        elif sw_version.startswith('BaiBS_QAFA'):
            return EnodebDeviceName.BAICELLS_QAFA
        elif sw_version.startswith('BaiStation_'):
            # Note: to disable flag inversion completely (for all builds),
            # set to BaiStation_V000R000C00B000SPC000
            # Note: to force flag inversion always (for all builds),
            # set to BaiStation_V999R999C99B999SPC999
            invert_before_version = \
                _parse_sw_version('BaiStation_V100R001C00B110SPC003')
            if _parse_sw_version(sw_version) < invert_before_version:
                return EnodebDeviceName.BAICELLS_OLD
            return EnodebDeviceName.BAICELLS
        elif sw_version.startswith('BaiBS_RTS_'):
            return EnodebDeviceName.BAICELLS
        else:
            raise KeyError("Device %s unsupported: Software (%s)" %
                           (device_oui, sw_version))
    elif device_oui in {'000FB7', }:
        return EnodebDeviceName.CAVIUM
    else:
        raise KeyError("Device %s unsupported" % device_oui)


def _parse_sw_version(version_str):
    """
    Parse SW version string.
    Expects format: BaiStation_V100R001C00B110SPC003
    For the above version string, returns: [100, 1, 0, 110, 3]
    Note: trailing characters (for dev builds) are ignored. Null is returned
    for version strings that don't match the above format.
    """
    logging.debug('Got firmware version: %s', version_str)

    version = re.findall(
        r'BaiStation_V(\d{3})R(\d{3})C(\d{2})B(\d{3})SPC(\d{3})', version_str)
    if not version:
        return None
    elif len(version) > 1:
        logging.warning('SW version (%s) not formatted as expected',
                        version_str)
    version_int = []
    for num in version[0]:
        try:
            version_int.append(int(num))
        except ValueError:
            logging.warning('SW version (%s) not formatted as expected',
                            version_str)
            return None

    logging.debug('Parsed firmware version: %s', version_int)

    return version_int
