#!/usr/bin/env python3
"""
BDMT XML Parser Module
Parses Blu-ray bdmt_*.xml metadata files to extract disc title like BDInfo
"""

import xml.etree.ElementTree as ET
import os
from typing import Optional
from pathlib import Path


class BDMTMetadata:
    """
    Object containing information on Blu-ray bdmt_*.xml files
    """
    def __init__(self, filename: str):
        """
        Parse a Blu-ray bdmt_*.xml metadata file to extract disc title
        :param str filename: path to the bdmt_*.xml file to be parsed
        :raises ValueError: if parsing fails
        :raises FileNotFoundError: if file doesn't exist
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"BDMT file not found: {filename}")

        self.filename = filename
        self.disc_title = None

        # Parse disc title from bdmt_*.xml file like BDInfo does
        try:
            tree = ET.parse(filename)
            root = tree.getroot()

            # Register namespace like BDInfo does
            ns = {'di': 'urn:BDA:bdmv;discinfo'}

            # Look for disc title in the XML structure
            # Path: discinfo -> title -> name
            title_node = root.find('.//di:discinfo/di:title/di:name', ns)
            if title_node is not None and title_node.text:
                title = title_node.text.strip()
                # Filter out generic titles like "Blu-ray" like BDInfo does
                if title and title.lower() != "blu-ray":
                    self.disc_title = title

        except Exception:
            # Silently fail if XML parsing fails, like BDInfo
            self.disc_title = None

    def __repr__(self):
        title = self.disc_title or "Unknown Title"
        return f"<BDMTMetadata title='{title}'>"


def find_bdmt_eng_file(directory: str) -> Optional[str]:
    """
    Find bdmt_eng.xml file in Blu-ray directory structure like BDInfo
    :param str directory: directory to search
    :rtype: str or None
    """
    directory_path = Path(directory)

    # Standard Blu-ray structure - BDInfo only looks for bdmt_eng.xml
    bdmt_path = directory_path / "BDMV" / "META" / "bdmt_eng.xml"
    if bdmt_path.exists():
        return str(bdmt_path)

    # Alternative location
    bdmt_path = directory_path / "META" / "bdmt_eng.xml"
    if bdmt_path.exists():
        return str(bdmt_path)

    # Check case variations
    for path in directory_path.rglob("bdmt_eng.xml"):
        return str(path)
    for path in directory_path.rglob("BDMT_ENG.XML"):
        return str(path)

    return None


def get_disc_title(directory: str) -> Optional[str]:
    """
    Get disc title from bdmt_eng.xml file like BDInfo does
    :param str directory: directory containing Blu-ray structure
    :rtype: str or None
    """
    try:
        bdmt_file = find_bdmt_eng_file(directory)
        if not bdmt_file:
            return None

        metadata = BDMTMetadata(bdmt_file)
        return metadata.disc_title

    except Exception:
        # Silently fail like BDInfo does
        return None
