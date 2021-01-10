# export as owl

```
robot template --template uo_template.csv -i unit.obo --prefix "RO:http://purl.obolibrary.org/obo/RO_" --prefix "UO:http://purl.obolibrary.org/obo/UO_" --prefix "obo:http://purl.obolibrary.org/obo/uo#"  --ontology-iri "http://purl.obolibrary.org/obo/uo.owl" convert --format ofn -o output/uo_template.owl
```
prefix "obo:http://purl.obolibrary.org/obo/"



uo.owl: http://purl.obolibrary.org/obo/is_unit_of http://purl.obolibrary.org/obo/has_prefix
unit.obo http://purl.obolibrary.org/obo/uo#is_unit_of


uo_template:
http://purl.obolibrary.org/obo/is_unit_of http://purl.obolibrary.org/obo/has_prefix
http://purl.obolibrary.org/obo/uo#is_unit_of


http://purl.obolibrary.org/obo/pato#is_unit_of
