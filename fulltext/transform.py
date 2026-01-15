import os
from lxml import etree

# Path configuration
base_folder = "fulltext"
xml_filename = os.path.join(base_folder, "script.xml")
xsl_filename = os.path.join(base_folder, "scriptstyle.xsl")
output_filename = os.path.join(base_folder, "scott_scene.html")

def main():
    if not os.path.exists(xml_filename):
        print(f"Error: {xml_filename} not found.")
        return
    if not os.path.exists(xsl_filename):
        print(f"Error: {xsl_filename} not found.")
        return

    try:
        # Load XML and XSLT
        dom = etree.parse(xml_filename)
        xslt = etree.parse(xsl_filename)

        # Apply transformation
        transform = etree.XSLT(xslt)
        new_dom = transform(dom)

        # Write output
        with open(output_filename, "wb") as f:
            f.write(etree.tostring(new_dom, pretty_print=True, method="html"))
        
        print(f"Success! Created: {output_filename}")

    except Exception as e:
        print(f"Transformation failed: {e}")

if __name__ == "__main__":
    main()