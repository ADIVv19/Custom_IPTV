import requests
import gzip
import xmltv
import io
from xml.etree import ElementTree as ET
from datetime import datetime

# List of EPG URLs
epg_urls = [
    "https://epgshare01.online/epgshare01/epg_ripper_CA1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_FANDUEL1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_US_SPORTS1.xml.gz"
]

def download_and_decompress(url):
    """Download and decompress a .xml.gz file, return ElementTree root."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with gzip.GzipFile(fileobj=io.BytesIO(response.content), mode='rb') as gz:
            return ET.parse(gz).getroot()
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None

def merge_epgs():
    """Merge multiple EPGs into one."""
    combined_channels = {}
    combined_programmes = []

    for url in epg_urls:
        root = download_and_decompress(url)
        if root is None:
            continue

        # Parse channels
        for channel in root.findall('channel'):
            id = channel.get('id')
            if id not in combined_channels:
                combined_channels[id] = channel

        # Parse programmes
        for programme in root.findall('programme'):
            combined_programmes.append(programme)

    # Create new XMLTV document
    tv = ET.Element('tv')
    tv.set('generator-info-name', 'Combined EPG')
    tv.set('generator-info-url', 'https://github.com/your-username/combined-epg')

    # Add channels
    for channel in combined_channels.values():
        tv.append(channel)

    # Add programmes
    for programme in combined_programmes:
        tv.append(programme)

    return tv

def save_compressed_xml(tree, output_file):
    """Save ElementTree as compressed .xml.gz."""
    with gzip.open(output_file, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)

def main():
    # Merge EPGs
    combined_tv = merge_epgs()

    # Save to file
    output_file = 'combined_epg.xml.gz'
    save_compressed_xml(ET.ElementTree(combined_tv), output_file)
    print(f"Combined EPG saved to {output_file}")

if __name__ == "__main__":
    main()