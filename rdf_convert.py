# ======== Base Configuration ========= #
import csv
import os
from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD

# All Namespaces
NS = {
    "sp": Namespace("https://scottpilgrim.org/resource/"),
    "bf": Namespace("http://id.loc.gov/ontologies/bibframe/"),
    "dcterms": Namespace("http://purl.org/dc/terms/"),
    "foaf": Namespace("http://xmlns.com/foaf/0.1/"),
    "gn": Namespace("http://www.geonames.org/ontology#"),
    "owl": Namespace("http://www.w3.org/2002/07/owl#"),
    "rdfs": Namespace("http://www.w3.org/2000/01/rdf-schema#"),
    "schema": Namespace("https://schema.org/"),
    "skos": Namespace("http://www.w3.org/2004/02/skos/core#"),
    "mo": Namespace("http://purl.org/ontology/mo/"),
    "rel": Namespace("http://purl.org/vocab/relationship/"),
    "rdf": Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    "org": Namespace("http://www.w3.org/ns/org#")
}

def init_graph():
    g = Graph()
    for prefix, ns in NS.items():
        g.bind(prefix, ns)
    return g

g = init_graph()

def get_sp_uri(val):
    if not val: return None
    return NS["sp"][val.replace("local:", "").strip()]

# ======== INDIVIDUAL FILE PROCESSING (MANUAL) ========= #

# 1. PPL.csv (Characters & Persons)
if os.path.exists("PPL.csv"):
    with open("PPL.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Subject definition
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type 
            if row.get("rdf:type"):
                type_prefix, type_term = row["rdf:type"].split(':')
                g.add((sub, RDF.type, NS[type_prefix][type_term]))
            else:
                # Fallback logic if rdf:type is empty
                g.add((sub, RDF.type, NS["schema"]["FictionalCharacter"] if "char_" in row["id"] else NS["foaf"]["Person"]))

            # 2. foaf:name (Literal)
            if row.get("foaf:name"):
                g.add((sub, NS["foaf"]["name"], Literal(row["foaf:name"])))

            # 3. schema:roleName (Literal - Protagonist, Support etc.)
            if row.get("schema:roleName"):
                g.add((sub, NS["schema"]["roleName"], Literal(row["schema:roleName"])))

            # 4. schema:portrayedBy (URI - Linked to another Person)
            if row.get("schema:portrayedBy"):
                g.add((sub, NS["schema"]["portrayedBy"], get_sp_uri(row["schema:portrayedBy"])))

            # 5. org:memberOf (URI - Linked to a Group/Band)
            if row.get("org:memberOf"):
           
                for group in row["org:memberOf"].split(';'):
                    g.add((sub, NS["org"]["memberOf"], get_sp_uri(group)))

            # 6. owl:sameAs (URIRef - Wikidata/External Links)
            if row.get("owl:sameAs"):
                g.add((sub, NS["owl"]["sameAs"], URIRef(row["owl:sameAs"])))

            # 7. foaf:page (URIRef - Fandom/Web pages)
            if row.get("foaf:page"):
                g.add((sub, NS["foaf"]["page"], URIRef(row["foaf:page"])))

            # 8. dcterms:isPartOf (URI - Linked to the Universe)
            if row.get("dcterms:isPartOf"):
                g.add((sub, NS["dcterms"]["isPartOf"], get_sp_uri(row["dcterms:isPartOf"])))

# 2. RLTNS.csv (Relationships)
if os.path.exists("RLTNS.csv"):
    with open("RLTNS.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:

            sub = get_sp_uri(row.get("Subject"))
            if not sub: 
                continue

 
            relations = [
                "rel:lifePartnerOf", 
                "rel:ambivalentOf", 
                "rel:friendOf", 
                "rel:livesWith", 
                "rel:antagonistOf",
                "org:memberOf"
            ]

            for p in relations:
                val = row.get(p)
                if val:
                    prefix, term = p.split(':')
                    targets = val.split(';')
                    for target in targets:
                        target_uri = get_sp_uri(target)
                        if target_uri:
                            g.add((sub, NS[prefix][term], target_uri))

# 3. ANIM.csv (Anime Series) 
if os.path.exists("ANIM.csv"):
    with open("ANIM.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Subject URI
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type
            if row.get("rdf:type"):
                p_parts = row["rdf:type"].split(':')
                g.add((sub, RDF.type, NS[p_parts[0]][p_parts[1]]))

            # 2. dcterms:title (Literal)
            if row.get("dcterms:title"):
                g.add((sub, NS["dcterms"]["title"], Literal(row["dcterms:title"])))

            # 3. schema:director (Literal)
            if row.get("schema:director"):
                g.add((sub, NS["schema"]["director"], Literal(row["schema:director"])))

            # 4. schema:screenwriter 
            if row.get("schema:screenwriter"):
                for writer in row["schema:screenwriter"].split(';'):
                    g.add((sub, NS["schema"]["screenwriter"], Literal(writer.strip())))

            # 5. schema:productionCompany 
            if row.get("schema:productionCompany"):
                for company in row["schema:productionCompany"].split(';'):
                    g.add((sub, NS["schema"]["productionCompany"], Literal(company.strip())))

            # 6. schema:broadcaster
            if row.get("schema:broadcaster"):
                g.add((sub, NS["schema"]["broadcaster"], Literal(row["schema:broadcaster"])))

            # 7. schema:datePublished
            if row.get("schema:datePublished"):
                g.add((sub, NS["schema"]["datePublished"], Literal(row["schema:datePublished"], datatype=XSD.gYear)))

            # 8. schema:numberOfSeasons 
            if row.get("schema:numberOfSeasons"):
                g.add((sub, NS["schema"]["numberOfSeasons"], Literal(row["schema:numberOfSeasons"], datatype=XSD.integer)))

            # 9. schema:numberOfEpisodes 
            if row.get("schema:numberOfEpisodes"):
                g.add((sub, NS["schema"]["numberOfEpisodes"], Literal(row["schema:numberOfEpisodes"], datatype=XSD.integer)))

            # 10. schema:genre 
            if row.get("schema:genre"):
                for genre in row["schema:genre"].split(';'):
                    g.add((sub, NS["schema"]["genre"], Literal(genre.strip())))

            # 11. schema:isBasedOn
            if row.get("schema:isBasedOn"):
                g.add((sub, NS["schema"]["isBasedOn"], get_sp_uri(row["schema:isBasedOn"])))

            # 12. dcterms:identifier 
            if row.get("dcterms:identifier"):
                g.add((sub, NS["dcterms"]["identifier"], URIRef(row["dcterms:identifier"])))

# 4. CMC.csv (Comic Series) 
if os.path.exists("CMC.csv"):
    with open("CMC.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Subject URI
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type 
            if row.get("rdf:type"):
                p_parts = row["rdf:type"].split(':')
                g.add((sub, RDF.type, NS[p_parts[0]][p_parts[1]]))

            # 2. dcterms:title (Literal)
            if row.get("dcterms:title"):
                g.add((sub, NS["dcterms"]["title"], Literal(row["dcterms:title"])))

            # 3. schema:author (Literal)
            if row.get("schema:author"):
                g.add((sub, NS["schema"]["author"], Literal(row["schema:author"])))

            # 4. schema:publisher
            if row.get("schema:publisher"):
                g.add((sub, NS["schema"]["publisher"], Literal(row["schema:publisher"])))

            # 5. schema:startDate (Literal - xsd:gYear)
            if row.get("schema:startDate"):
                g.add((sub, NS["schema"]["startDate"], Literal(row["schema:startDate"], datatype=XSD.gYear)))

            # 6. schema:endDate (Literal - xsd:gYear)
            if row.get("schema:endDate"):
                g.add((sub, NS["schema"]["endDate"], Literal(row["schema:endDate"], datatype=XSD.gYear)))

            # 7. schema:numberOfVolumes (Literal - xsd:integer)
            if row.get("schema:numberOfVolumes"):
                g.add((sub, NS["schema"]["numberOfVolumes"], Literal(row["schema:numberOfVolumes"], datatype=XSD.integer)))

            # 8. schema:genre 
            if row.get("schema:genre"):
                for genre in row["schema:genre"].split(';'):
                    g.add((sub, NS["schema"]["genre"], Literal(genre.strip())))

            # 9. dcterms:identifier (URIRef - Wikidata URL)
            if row.get("dcterms:identifier"):
                g.add((sub, NS["dcterms"]["identifier"], URIRef(row["dcterms:identifier"])))

# 5. STRCTR.csv (Soundtrack & Songs) 
if os.path.exists("STRCTR.csv"):
    with open("STRCTR.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            
            sub = get_sp_uri(row.get("id") or row.get("Subject"))
            if not sub: continue
            
            # 1. rdf:type
            if row.get("rdf:type"):
                p_parts = row["rdf:type"].split(':')
                g.add((sub, RDF.type, NS[p_parts[0]][p_parts[1]]))
            
            # 2. dcterms:title (Literal)
            if row.get("dcterms:title"):
                g.add((sub, NS["dcterms"]["title"], Literal(row["dcterms:title"])))
                
            # 3. schema:producer 
            if row.get("schema:producer"):
                g.add((sub, NS["schema"]["producer"], Literal(row["schema:producer"])))
                
            # 4. schema:performer 
            if row.get("schema:performer"):
                for perf in row["schema:performer"].split(';'):
                    target_uri = get_sp_uri(perf.strip())
                    if target_uri:
                        g.add((sub, NS["schema"]["performer"], target_uri))
                    
            # 5. schema:datePublished (Literal - xsd:gYear)
            if row.get("schema:datePublished"):
                g.add((sub, NS["schema"]["datePublished"], Literal(row["schema:datePublished"], datatype=XSD.gYear)))
                
            # 6. dcterms:format 
            if row.get("dcterms:format"):
                for fmt in row["dcterms:format"].split(';'):
                    g.add((sub, NS["dcterms"]["format"], Literal(fmt.strip())))
                    
            # 7. schema:genre 
            if row.get("schema:genre"):
                for genre in row["schema:genre"].split(';'):
                    g.add((sub, NS["schema"]["genre"], Literal(genre.strip())))
                    
            # 8. dcterms:isPartOf 
            if row.get("dcterms:isPartOf"):
                g.add((sub, NS["dcterms"]["isPartOf"], get_sp_uri(row["dcterms:isPartOf"])))
                
            # 9. owl:sameAs
            if row.get("owl:sameAs"):
                g.add((sub, NS["owl"]["sameAs"], URIRef(row["owl:sameAs"])))

# 6. SNDTRCK.csv (Soundtrack & Music Recordings) 
if os.path.exists("SNDTRCK.csv"):
    with open("SNDTRCK.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
          
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type 
            if row.get("rdf:type"):
                p_parts = row["rdf:type"].split(':')
                g.add((sub, RDF.type, NS[p_parts[0]][p_parts[1]]))
            
            # 2. dcterms:title (Literal)
            if row.get("dcterms:title"):
                g.add((sub, NS["dcterms"]["title"], Literal(row["dcterms:title"])))
                
            # 3. schema:producer (Literal)
            if row.get("schema:producer"):
                g.add((sub, NS["schema"]["producer"], Literal(row["schema:producer"])))
                
            # 4. schema:performer 
            if row.get("schema:performer"):
                for perf in row["schema:performer"].split(';'):
                    target_uri = get_sp_uri(perf.strip())
                    if target_uri:
                        g.add((sub, NS["schema"]["performer"], target_uri))
                    
            # 5. schema:datePublished (Literal - xsd:gYear)
            if row.get("schema:datePublished"):
                g.add((sub, NS["schema"]["datePublished"], Literal(row["schema:datePublished"], datatype=XSD.gYear)))
                
            # 6. dcterms:format (Literal - CD, Digital)
            if row.get("dcterms:format"):
                for fmt in row["dcterms:format"].split(';'):
                    g.add((sub, NS["dcterms"]["format"], Literal(fmt.strip())))
                    
            # 7. schema:genre (Literal - Indie Rock, Punk)
            if row.get("schema:genre"):
                for genre in row["schema:genre"].split(';'):
                    g.add((sub, NS["schema"]["genre"], Literal(genre.strip())))
                    
            # 8. dcterms:isPartOf 
            if row.get("dcterms:isPartOf"):
                g.add((sub, NS["dcterms"]["isPartOf"], get_sp_uri(row["dcterms:isPartOf"])))
                
            # 9. owl:sameAs 
            if row.get("owl:sameAs"):
                g.add((sub, NS["owl"]["sameAs"], URIRef(row["owl:sameAs"])))

# 7. GTR.csv (Guitars & Instruments) 
if os.path.exists("GTR.csv"):
    with open("GTR.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type (mo:Instrument)
            if row.get("rdf:type"):
                p_parts = row["rdf:type"].split(':')
                g.add((sub, RDF.type, NS[p_parts[0]][p_parts[1]]))
            
            # 2. foaf:name 
            if row.get("foaf:name"):
                g.add((sub, NS["foaf"]["name"], Literal(row["foaf:name"])))

            # 3. dcterms:description (Literal)
            if row.get("dcterms:description"):
                g.add((sub, NS["dcterms"]["description"], Literal(row["dcterms:description"])))

            # 4. schema:ownedBy 
            if row.get("schema:ownedBy"):
                g.add((sub, NS["schema"]["ownedBy"], get_sp_uri(row["schema:ownedBy"])))

            # 5. schema:brand 
            if row.get("schema:brand"):
                g.add((sub, NS["schema"]["brand"], Literal(row["schema:brand"])))

            # 6. schema:productionDate 
            if row.get("schema:productionDate"):
                g.add((sub, NS["schema"]["productionDate"], Literal(row["schema:productionDate"])))

            # 7. schema:material 
            if row.get("schema:material"):
                for material in row["schema:material"].split(';'):
                    g.add((sub, NS["schema"]["material"], Literal(material.strip())))

            # 8. schema:color 
            if row.get("schema:color"):
                g.add((sub, NS["schema"]["color"], Literal(row["schema:color"])))

            # 9. owl:sameAs (URIRef - Wikidata link)
            if row.get("owl:sameAs"):
                g.add((sub, NS["owl"]["sameAs"], URIRef(row["owl:sameAs"])))

# 8. CSLM.csv (Landmarks & Locations)
if os.path.exists("CSLM.csv"):
    with open("CSLM.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
        
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type (schema:LandmarksOrHistoricalBuildings)
            if row.get("rdf:type"):
                p_parts = row["rdf:type"].split(':')
                g.add((sub, RDF.type, NS[p_parts[0]][p_parts[1]]))
            
            # 2. foaf:name 
            if row.get("foaf:name"):
                g.add((sub, NS["foaf"]["name"], Literal(row["foaf:name"])))

            # 3. dcterms:description 
            if row.get("dcterms:description"):
                g.add((sub, NS["dcterms"]["description"], Literal(row["dcterms:description"])))

            # 4. schema:address 
            if row.get("schema:address"):
                g.add((sub, NS["schema"]["address"], Literal(row["schema:address"])))

            # 5. schema:architect 
            if row.get("schema:architect"):
                g.add((sub, NS["schema"]["architect"], Literal(row["schema:architect"])))

            # 6. schema:dateCreated 
            if row.get("schema:dateCreated"):
                g.add((sub, NS["schema"]["dateCreated"], Literal(row["schema:dateCreated"])))

            # 7. dcterms:isPartOf 
            if row.get("dcterms:isPartOf"):
                g.add((sub, NS["dcterms"]["isPartOf"], get_sp_uri(row["dcterms:isPartOf"])))

            # 8. owl:sameAs 
            if row.get("owl:sameAs"):
                g.add((sub, NS["owl"]["sameAs"], URIRef(row["owl:sameAs"])))

# 9. GRPS.csv (Groups & Organizations)
if os.path.exists("GRPS.csv"):
    with open("GRPS.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
           
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type 
            if row.get("rdf:type"):
                p_parts = row["rdf:type"].split(':')
                g.add((sub, RDF.type, NS[p_parts[0]][p_parts[1]]))
            
            # 2. foaf:name 
            if row.get("foaf:name"):
                g.add((sub, NS["foaf"]["name"], Literal(row["foaf:name"])))

            # 3. dcterms:description 
            if row.get("dcterms:description"):
                g.add((sub, NS["dcterms"]["description"], Literal(row["dcterms:description"])))

            # 4. owl:sameAs 
            if row.get("owl:sameAs"):
                g.add((sub, NS["owl"]["sameAs"], URIRef(row["owl:sameAs"])))

# 10. PLMTR.csv (Plumtree & Inspirations)
if os.path.exists("PLMTR.csv"):
    with open("PLMTR.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
           
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type 
            if row.get("rdf:type"):
                p_parts = row["rdf:type"].split(':')
                g.add((sub, RDF.type, NS[p_parts[0]][p_parts[1]]))
            
            # 2. dcterms:title (Literal)
            if row.get("dcterms:title"):
                g.add((sub, NS["dcterms"]["title"], Literal(row["dcterms:title"])))

            # 3. mo:performer (
            if row.get("mo:performer"):
                g.add((sub, NS["mo"]["performer"], URIRef(row["mo:performer"])))

            # 4. mo:genre 
            if row.get("mo:genre"):
                g.add((sub, NS["mo"]["genre"], Literal(row["mo:genre"])))

            # 5. dcterms:issued (Literal - xsd:gYear)
            if row.get("dcterms:issued"):
                g.add((sub, NS["dcterms"]["issued"], Literal(row["dcterms:issued"], datatype=XSD.gYear)))

            # 6. dcterms:medium 
            if row.get("dcterms:medium"):
                g.add((sub, NS["dcterms"]["medium"], Literal(row["dcterms:medium"])))

            # 7. dcterms:extent 
            if row.get("dcterms:extent"):
                g.add((sub, NS["dcterms"]["extent"], Literal(row["dcterms:extent"])))

            # 8. mo:publisher (Literal - Cinnamon Toast Records)
            if row.get("mo:publisher"):
                g.add((sub, NS["mo"]["publisher"], Literal(row["mo:publisher"])))

            # 9. dcterms:description (Literal)
            if row.get("dcterms:description"):
                g.add((sub, NS["dcterms"]["description"], Literal(row["dcterms:description"])))

            # 10. dcterms:isPartOf 
            if row.get("dcterms:isPartOf"):
                g.add((sub, NS["dcterms"]["isPartOf"], get_sp_uri(row["dcterms:isPartOf"])))

            # 11. owl:sameAs 
            if row.get("owl:sameAs"):
                g.add((sub, NS["owl"]["sameAs"], URIRef(row["owl:sameAs"])))

# 11. SCTT_MV.csv (Movie Details)
if os.path.exists("SCTT_MV.csv"):
    with open("SCTT_MV.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type 
            if row.get("rdf:type"):
                g.add((sub, RDF.type, URIRef(row["rdf:type"])))
            
            # 2. dcterms:title (Literal)
            if row.get("dcterms:title"):
                g.add((sub, NS["dcterms"]["title"], Literal(row["dcterms:title"])))
                
            # 3. schema:director 
            if row.get("schema:director"):
                g.add((sub, NS["schema"]["director"], URIRef(row["schema:director"])))
                
            # 4. schema:actor 
            if row.get("schema:actor"):
                for actor_url in row["schema:actor"].split(';'):
                    g.add((sub, NS["schema"]["actor"], URIRef(actor_url.strip())))
                    
            # 5. schema:datePublished (Literal - xsd:gYear)
            if row.get("schema:datePublished"):
                g.add((sub, NS["schema"]["datePublished"], Literal(row["schema:datePublished"], datatype=XSD.gYear)))
                
            # 6. schema:isBasedOn 
            if row.get("schema:isBasedOn"):
                g.add((sub, NS["schema"]["isBasedOn"], get_sp_uri(row["schema:isBasedOn"])))
                
            # 7. schema:locationCreated 
            if row.get("schema:locationCreated"):
                g.add((sub, NS["schema"]["locationCreated"], get_sp_uri(row["schema:locationCreated"])))
                
            # 8. schema:musicBy 
            if row.get("schema:musicBy"):
                g.add((sub, NS["schema"]["musicBy"], get_sp_uri(row["schema:musicBy"])))
                
            # 9. dcterms:identifier 
            if row.get("dcterms:identifier"):
                g.add((sub, NS["dcterms"]["identifier"], URIRef(row["dcterms:identifier"])))
                
            # 10. schema:screenwriter 
            if row.get("schema:screenwriter"):
                for writer in row["schema:screenwriter"].split(';'):
                    g.add((sub, NS["schema"]["screenwriter"], Literal(writer.strip())))
                    
            # 11. schema:genre 
            if row.get("schema:genre"):
                for genre in row["schema:genre"].split(';'):
                    g.add((sub, NS["schema"]["genre"], Literal(genre.strip())))
                    
            # 12. schema:productionCompany 
            if row.get("schema:productionCompany"):
                for company in row["schema:productionCompany"].split(';'):
                    g.add((sub, NS["schema"]["productionCompany"], Literal(company.strip())))
                    
            # 13. schema:duration 
            if row.get("schema:duration"):
                g.add((sub, NS["schema"]["duration"], Literal(row["schema:duration"])))

# 12. PSTR.csv (Posters & Media Objects) 
if os.path.exists("PSTR.csv"):
    with open("PSTR.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type (schema:ImageObject)
            if row.get("rdf:type"):
                p_parts = row["rdf:type"].split(':')
                g.add((sub, RDF.type, NS[p_parts[0]][p_parts[1]]))
            
            # 2. dcterms:title 
            if row.get("dcterms:title"):
                g.add((sub, NS["dcterms"]["title"], Literal(row["dcterms:title"])))

            # 3. schema:creator 
            if row.get("schema:creator"):
                g.add((sub, NS["schema"]["creator"], Literal(row["schema:creator"])))

            # 4. schema:dateCreated (Literal - xsd:gYear)
            if row.get("schema:dateCreated"):
                g.add((sub, NS["schema"]["dateCreated"], Literal(row["schema:dateCreated"], datatype=XSD.gYear)))

            # 5. dcterms:format 
            if row.get("dcterms:format"):
                g.add((sub, NS["dcterms"]["format"], Literal(row["dcterms:format"])))

            # 6. dcterms:isPartOf 
            if row.get("dcterms:isPartOf"):
                g.add((sub, NS["dcterms"]["isPartOf"], get_sp_uri(row["dcterms:isPartOf"])))

            # 7. schema:url 
            if row.get("schema:url"):
                g.add((sub, NS["schema"]["url"], URIRef(row["schema:url"])))

# 13. SCRPT.csv (Screenplay & Creative Works) 
if os.path.exists("SCRPT.csv"):
    with open("SCRPT.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type 
            if row.get("rdf:type"):
                p_parts = row["rdf:type"].split(':')
                g.add((sub, RDF.type, NS[p_parts[0]][p_parts[1]]))
            
            # 2. dcterms:title 
            if row.get("dcterms:title"):
                g.add((sub, NS["dcterms"]["title"], Literal(row["dcterms:title"])))

            # 3. schema:author 
            if row.get("schema:author"):
                for author in row["schema:author"].split(';'):
                    g.add((sub, NS["schema"]["author"], Literal(author.strip())))

            # 4. dcterms:language 
            if row.get("dcterms:language"):
                g.add((sub, NS["dcterms"]["language"], Literal(row["dcterms:language"])))

            # 5. dcterms:format 
            if row.get("dcterms:format"):
                g.add((sub, NS["dcterms"]["format"], Literal(row["dcterms:format"])))

            # 6. schema:dateCreated (Literal - xsd:gYear)
            if row.get("schema:dateCreated"):
                g.add((sub, NS["schema"]["dateCreated"], Literal(row["schema:dateCreated"], datatype=XSD.gYear)))

            # 7. dcterms:isPartOf 
            if row.get("dcterms:isPartOf"):
                g.add((sub, NS["dcterms"]["isPartOf"], get_sp_uri(row["dcterms:isPartOf"])))

            # 8. owl:sameAs 
            if row.get("owl:sameAs"):
                g.add((sub, NS["owl"]["sameAs"], URIRef(row["owl:sameAs"])))

# 14. VDGM.csv (Video Game) 
if os.path.exists("VDGM.csv"):
    with open("VDGM.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            
            sub = NS["sp"][row["id"]]
            
            # 1. rdf:type 
            if row.get("rdf:type"):
                
                type_val = row["rdf:type"]
                if "schema" in type_val and ":" not in type_val:
                    g.add((sub, RDF.type, NS["schema"]["VideoGame"]))
                elif ":" in type_val:
                    p_parts = type_val.split(':')
                    g.add((sub, RDF.type, NS[p_parts[0]][p_parts[1]]))

            # 2. dcterms:title (Literal)
            if row.get("dcterms:title"):
                g.add((sub, NS["dcterms"]["title"], Literal(row["dcterms:title"])))

            # 3. schema:publisher (Literal - Ubisoft)
            if row.get("schema:publisher"):
                g.add((sub, NS["schema"]["publisher"], Literal(row["schema:publisher"])))

            # 4. schema:genre (Literal - Beat 'em up)
            if row.get("schema:genre"):
                g.add((sub, NS["schema"]["genre"], Literal(row["schema:genre"])))

            # 5. schema:gamePlatform 
            if row.get("schema:gamePlatform"):
                for platform in row["schema:gamePlatform"].split(';'):
                    g.add((sub, NS["schema"]["gamePlatform"], Literal(platform.strip())))

            # 6. schema:datePublished (Literal - xsd:gYear)
            if row.get("schema:datePublished"):
                g.add((sub, NS["schema"]["datePublished"], Literal(row["schema:datePublished"], datatype=XSD.gYear)))

            # 7. schema:isBasedOn 
            if row.get("schema:isBasedOn"):
                
                val = row["schema:isBasedOn"]
                if "local" in val and ":" not in val:
                    val = val.replace("local", "local:")
                g.add((sub, NS["schema"]["isBasedOn"], get_sp_uri(val)))

            # 8. dcterms:identifier (URIRef - Wikidata linki)
            if row.get("dcterms:identifier"):
                g.add((sub, NS["dcterms"]["identifier"], URIRef(row["dcterms:identifier"])))

# ======== Final Serialization ========= #
g.serialize(destination="scott_pilgrim_master.ttl", format="turtle")
print("Process completed. All 14 files processed individually.")