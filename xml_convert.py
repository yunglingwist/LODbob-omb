from rdflib import Graph

g = Graph()

g.parse("scott_pilgrim_master.ttl", format="turtle")


g.serialize(destination="scott_pilgrim_master.xml", format="pretty-xml")

print("Conversion completed successfully: scott_pilgrim_master.xml")