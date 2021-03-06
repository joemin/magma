"""
Copyright (c) 2016-present, Facebook, Inc.
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

from enum import Enum
from typing import Optional


class DuplexMode(Enum):
    FDD = 1
    TDD = 2


class LTEBandInfo:
    """ Class for holding information related to LTE band.
        Takes advantage of the following properties of LTE EARFCN assignment:
            - EARFCN spacing within a band is always 0.1MHz
            - 1:1 mapping between EARFCNDL and EARFCNUL (for FDD)
    """
    def __init__(self, duplex_mode, earfcndl, start_freq_dl_mhz,
                 start_earfcnul=None, start_freq_ul_mhz=None):
        """
        Inputs:
        - Duplex mode - type = DuplexMode
        - earfcndl - List/generator of integer EARFCNDLs in band, from lowest to
                     highest
        - start_freq_dl_mhz - Frequency of lowest numbered EARFCNDL in band
                            (MHz)
        - start_earfcnul - Lowest numbered EARFCNUL in band
                            (or None if band is TDD)
        - start_freq_ul_mhz - Frequency of lowest numbered EARFCNUL in band
                              (MHz) (or None if band is TDD)
        """
        # Validate inputs
        assert type(earfcndl) == list or type(earfcndl) == range
        assert type(start_freq_dl_mhz) == int
        assert type(duplex_mode) == DuplexMode
        if duplex_mode == DuplexMode.FDD:
            assert type(start_earfcnul) == int
            assert type(start_freq_ul_mhz) == int
        else:
            assert start_earfcnul is None
            assert start_freq_ul_mhz is None

        # DuplexMode.TDD or DuplexMode.FDD
        self.duplex_mode = duplex_mode
        # Array of EARFCNDL values
        self.earfcndl = earfcndl
        # Array of DL frequencies in MHz, one per EARFCNDL
        self.freq_mhz_dl = [start_freq_dl_mhz + 0.1 * (earfcn - earfcndl[0])
                            for earfcn in earfcndl]

        if duplex_mode == DuplexMode.FDD:
            # Array of EARFCNUL values that map to EARFCNDL
            self.earfcnul = range(start_earfcnul,
                                  start_earfcnul + len(earfcndl))
            # Array of UL frequencies in MHz, one per EARFCNUL
            self.freq_mhz_ul = [start_freq_ul_mhz + 0.1 * (earfcn -
                                self.earfcnul[0]) for earfcn in self.earfcnul]
        else:
            self.earfcnul = None
            self.freq_mhz_ul = None


# See, for example, http://niviuk.free.fr/lte_band.php for LTE band info
LTE_BAND_INFO = {
    # FDD bands
    # duplex_mode, EARFCNDL, start_freq_dl, start_EARCNUL, start_freq_ul
    1: LTEBandInfo(DuplexMode.FDD, range(0, 600), 2110, 18000, 1920),
    2: LTEBandInfo(DuplexMode.FDD, range(600, 1200), 1930, 18600, 1850),
    3: LTEBandInfo(DuplexMode.FDD, range(1200, 1950), 1805, 19200, 1710),
    4: LTEBandInfo(DuplexMode.FDD, range(1950, 2400), 2110, 19950, 1710),
    5: LTEBandInfo(DuplexMode.FDD, range(2400, 2649), 869, 20400, 824),
    28: LTEBandInfo(DuplexMode.FDD, range(9210, 9660), 758, 27210, 703),
    # TDD bands
    # duplex_mode, EARFCNDL, start_freq_dl
    39: LTEBandInfo(DuplexMode.TDD, range(38250, 38650), 1880),
    40: LTEBandInfo(DuplexMode.TDD, range(38650, 39650), 2300),
    41: LTEBandInfo(DuplexMode.TDD, range(39650, 41590), 2496),
    42: LTEBandInfo(DuplexMode.TDD, range(41590, 43590), 3400),
    43: LTEBandInfo(DuplexMode.TDD, range(43590, 45590), 3600),
    48: LTEBandInfo(DuplexMode.TDD, range(55240, 56740), 3550),
}
# TODO - add remaining LTE bands


def map_earfcndl_to_duplex_mode(earfcndl: int) -> Optional[DuplexMode]:
    """
    Returns None if we do not support the EARFCNDL
    """
    for band in LTE_BAND_INFO.keys():
        if earfcndl in LTE_BAND_INFO[band].earfcndl:
            return LTE_BAND_INFO[band].duplex_mode
    return None


def map_earfcndl_to_band_earfcnul_mode(earfcndl):
    """ Inputs:
            - EARFCNDL (integer)
        Outputs:
            - Band (integer)
            - Mode (DuplexMode)
            - EARFCNUL (integer - or None if TDD)
    """
    for band in LTE_BAND_INFO.keys():
        if earfcndl in LTE_BAND_INFO[band].earfcndl:
            if LTE_BAND_INFO[band].duplex_mode == DuplexMode.FDD:
                index = LTE_BAND_INFO[band].earfcndl.index(earfcndl)
                earfcnul = LTE_BAND_INFO[band].earfcnul[index]
            else:
                earfcnul = None

            return band, LTE_BAND_INFO[band].duplex_mode, earfcnul

    raise ValueError('EARFCNDL %d not found in LTE band info' % earfcndl)
