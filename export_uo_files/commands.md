# unit.obo

## Export unit.obo: (the current edit file for UO)

```
robot export --input unit.obo \
  --header "ID|Type|LABEL|has_obo_namespace|SubClass Of|definition|hasDbXref|comment|hasExactSynonym|has_narrow_synonym|hasRelatedSynonym|created_by|creation_date|in_subset|has_alternative_id" \
  --include "classes properties" \
  --export unit_obo_export.csv
```

## Perpare Robot tempate from export

Modified `unit_obo_export.csv` into robot a template csv called `unit_obo_remake.csv` see https://docs.google.com/spreadsheets/d/1pMFHey07BsYW17TpniFUu0xMu3YI0Q9GanScAnlel8E/edit?usp=sharing



## Run robot template:

```
robot template --template unit_obo_remake.csv -i unit.obo --prefix "RO:http://purl.obolibrary.org/obo/RO_" --prefix "UO:http://purl.obolibrary.org/obo/UO_"  --ontology-iri "http://purl.obolibrary.org/obo/uo.owl" convert --format obo -o unit_obo_remake.obo
```


## compare against obo file

```
robot diff --left unit_obo_remake.obo --right unit.obo
```







# uo.owl

## Export uo.owl:

For now to get the DbXrefs from the comments to add to the definitions in the joined file emulate unit.obo

```
robot export --input uo.owl \
  --header "ID|LABEL|Type|SubClass Of|Equivalent Class|comment|hasExactSynonym|hasRelatedSynonym" \
  --include "classes properties" \
  --export uo_export.csv
```

```
robot export --input uo.owl \
  --header "ID|LABEL|Type|SubClass Of|Equivalent Class|comment|hasExactSynonym|hasRelatedSynonym" \
  --include "classes individuals properties" \
  --export uo_export.csv
```


## modify to make robot template:

save as `uo.owl_remake.csv`



# Run robot template:

```
robot template --template uo.owl_remake.csv -i unit.obo --prefix "RO:http://purl.obolibrary.org/obo/RO_" --prefix "UO:http://purl.obolibrary.org/obo/UO_" --prefix "PATO:http://purl.obolibrary.org/obo/PATO_" --prefix "obo:http://purl.obolibrary.org/obo/" --ontology-iri "http://purl.obolibrary.org/obo/uo.owl" -o uo.owl_remake.owl
```
doesn't work with uo.owl as input



## compare against obo file

```
robot diff --left uo.owl_remake.owl --right uo.owl > owl_diff.txt
```


2 issues:

1) pipes in hasExactSynonym for the NamedIndividuals are causing an error where you get a third synonym with the | in it e.g., `m|metre`

2) the hasExactSynonym are different

in uo.owl_remake.owl not in uo.owl we have:

- AnnotationAssertion(<http://www.geneontology.org/formats/oboInOwl#hasExactSynonym> <http://purl.obolibrary.org/obo/UO_0000003> "time derived unit"^^xsd:string)

vs

in uo.owl not in uo.owl_remake.owl we have:

+ AnnotationAssertion(<oboInOwl:hasExactSynonym> <http://purl.obolibrary.org/obo/UO_0000003> "time derived unit"^^xsd:string)


it's because in uo.owl the prefix is `xmlns:oboInOwl="oboInOwl:"` Which is in correct whereas in uo.owl_remake.owl it's `xmlns:oboInOwl="http://www.geneontology.org/formats/oboInOwl#">` I'm not sure how to recreate this but in robot but it seems pointless cause we should just do it correctly anyway. From this I've learned that we can pun in robot but we can't add the | delim synonyms but we don't need to as the instances wil inherit the synonyms from the classes. 
