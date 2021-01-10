# For uo.owl:

```
robot export --input uo.owl \
  --header "ID|LABEL|Type|SubClass Of|Equivalent Class|comment|hasExactSynonym|hasRelatedSynonym" \
  --include "classes individuals properties" \
  --export uo_export.csv
```

This will export all needed columns from all classes and individuals



# For unit.obo: (the current edit file for UO)

```
robot export --input unit.obo \
  --header "ID|LABEL|has_obo_namespace|SubClass Of|definition|hasDbXref|comment|hasExactSynonym|has_narrow_synonym|hasRelatedSynonym|created_by|creation_date|in_subset|has_alternative_id" \
  --export unit_obo_export.csv
```




# Convert unit.obo to owl


robot convert --input unit.obo --format ofn --output unit-obo.owl



# Export unit-obo.owl to csv
prob don't need this

```
robot export --input unit-obo.owl \
  --header "ID|LABEL|has_obo_namespace|SubClass Of|definition|hasDbXref|comment|hasExactSynonym|has_narrow_synonym|hasRelatedSynonym|created_by|creation_date|in_subset|has_alternative_id" \
  --export unit-obo-owl.csv
```

database_cross_reference doesn't work either to get the ap's on the definitions.
Using a diff checker, this (unit-obo-owl.csv) is identical to unit_obo_export.csv.



# For OM


copied OM to the file `om-2.0_en.rdf` where I used regex in atom to replace `<rdfs:label xml:lang="nl">.*</rdfs:label>`, `<rdfs:label xml:lang="zh">.*</rdfs:label>`, and `<rdfs:label xml:lang="ja">.*</rdfs:label>` with empty string.


```
robot export --input om-2.0_en.rdf \
  --header "ID|LABEL|comment|symbol|alternative label|alternative symbol|Type|longcomment" \
  --export om_en_export.xlsx
```

Save xlsx to: `om_export_xlsx.csv`

Notes:

* `Unable to find namespace for: http://www.ontology-of-units-of-measure.org/resource/om-2/Irradiance` many of these warnings, but we seem to have these so I think it's ok it's just a warning.

* exporting to csv and tsv will loose the non standard characters, html, json and xlsx won't. We'll do xlsx and resave in excel to get a csv with the characters to parse.

* unfortunately OM uses dulicate rdfs:label for synonyms e.g., `centimetre`, `centimeter` so Robot label or LABEL won't caputure the duplicates with | delim, maybe there's a way but I can work with it. I can use hamming distances or for meter and liter have special code that does both versions whenever it sees those strings. Instead I removed the Dutch and Chinese lang tags.

# For QUDT:

```
robot export --input VOCAB_QUDT-UNITS-ALL-v2.1.ttl \
  --prefix "rdfs:http://www.w3.org/2000/01/rdf-schema#" \
  --prefix "qudt:http://qudt.org/schema/qudt/" \
  --header "ID|LABEL|Type|ucumCode|description|expression|isDefinedBy|information reference|dbpedia match|latex definition|normative reference (ISO)|todo" \
  --export qudt_export.xlsx
```

Use this simpler one:

```
robot export --input VOCAB_QUDT-UNITS-ALL-v2.1.ttl \
  --header "ID|LABEL|Type|ucumCode|description|expression|isDefinedBy" \
  --export qudt_export.xlsx
```



--prefix "qudt:http://qudt.org/schema/qudt/"


rdfs:isDefinedBy

### old:

prefixes:   
`--prefix "rdfs:http://www.w3.org/2000/01/rdf-schema#" \` and `--prefix "owl:http://www.w3.org/2002/07/owl#" \` don't seem to affect the command


# `comment` works!

# Adding `SubClasses` threw an error
# `SubProperty Of` didn't have anything probably because there are no subproperties
# `Equivalent Property` gives nothing (expected)
# `Disjoint With` also nothing
# `Type` gives us both the classes and instances (as expected per the groovy routine)



# `SYNONYMS` didn't yield anything
# `rdfs:comment` didn't yield anything, but `rdfs:label` to figure out, even wit prefix doesn't work

# `http://www.w3.org/2000/01/rdf-schema#comment` didn't work either

# `oboInOwl:hasExactSynonym` didn't work

***

Some of these aren't working and I suspect it's UO's owl is incorrect trying with `envo-edit.owl`


```
robot export --input envo-edit.owl \
  --prefix "rdfs:http://www.w3.org/2000/01/rdf-schema#" \
  --prefix "owl:http://www.w3.org/2002/07/owl#" \
  --prefix "oboInOwl:http://www.geneontology.org/formats/oboInOwl#" \
  --header "ID|LABEL|SubClass Of|Equivalent Class|database_cross_reference" \
  --export envo_export.csv
```


`rdfs:comment` still didn't work same with `oboInOwl:hasDbXref` or `oboInOwl:hasExactSynonym`


`database_cross_reference` did work in ENVO where it's defined
