import json
from typing import Optional, Any, Dict
from fastapi import UploadFile
import logging
import xml.etree.ElementTree as ET
import os
import csv
from io import StringIO

logger = logging.getLogger(__name__)

async def load_file(file: UploadFile, file_format: Optional[str] = None) -> Optional[Dict[str, Any]]:
    content = await file.read()

    # Wenn kein Format angegeben ist, versuchen wir aus der Dateiendung das Format abzuleiten
    if not file_format:
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower().strip('.')
        file_format = ext if ext else 'json'  # Standard fallback json

    logger.info(f"Attempting to parse file with format: {file_format}")

    if file_format == "json":
        return parse_json(content)
    elif file_format in ["xml", "nmapxml"]:
        return parse_xml(content)
    elif file_format == "txt":
        return parse_text(content)
    elif file_format == "csv":
        return parse_csv(content)
    else:
        # Unbekanntes Format
        logger.error(f"Unknown or unsupported file format: {file_format}")
        return None

def parse_json(content: bytes) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return None

def parse_xml(content: bytes) -> Optional[Dict[str, Any]]:
    try:
        root = ET.fromstring(content)
        return xml_to_dict(root)
    except ET.ParseError as e:
        logger.error(f"XML parsing error: {e}")
        return None

def xml_to_dict(element: ET.Element) -> Dict[str, Any]:
    node_dict = {element.tag: {} if element.attrib else None}
    children = list(element)
    if children:
        dd = {}
        for dc in map(xml_to_dict, children):
            for k, v in dc.items():
                if k in dd:
                    if not isinstance(dd[k], list):
                        dd[k] = [dd[k]]
                    dd[k].append(v)
                else:
                    dd[k] = v
        node_dict = {element.tag: dd}
    if element.attrib:
        node_dict[element.tag].update(('@' + k, v) for k, v in element.attrib.items())
    if element.text and element.text.strip():
        text = element.text.strip()
        if children or element.attrib:
            node_dict[element.tag]['#text'] = text
        else:
            node_dict[element.tag] = text
    return node_dict

def parse_text(content: bytes) -> Dict[str, Any]:
    lines = content.decode('utf-8', errors='replace').splitlines()
    return {"lines": lines}

def parse_csv(content: bytes) -> Optional[Dict[str, Any]]:
    decoded_content = content.decode('utf-8', errors='replace')
    reader = csv.reader(StringIO(decoded_content))
    rows = [row for row in reader]
    return {"csv_data": rows}
