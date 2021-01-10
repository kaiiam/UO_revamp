Note that OM has some terms that are both classes and instances, I noticed this because terms matching PATO seem to have this pattern e.g.

```
http://www.ontology-of-units-of-measure.org/resource/om-2/Mass	mass	Mass is the amount of matter of a phenomenon. It is a base quantity in the International System of Units. Mass is force divided by acceleration.	m			Named individual
http://www.ontology-of-units-of-measure.org/resource/om-2/MassFlow	mass flow	Mass flow is the movement of substances at equal rates or as a single body.				Class
```

(shows that OM `mass` is both Named individual and a Class)

Have the mapping seperated by only UO terms but it works mostly for PATO too so we could do a seperate pass for mapping PATO to OM could suggest this at the meeting.



including regex_OM_ID_per = r"http://www.ontology-of-units-of-measure.org/resource/om-2/([\w]*)Per([\w]*)" was getting some extra undesirable matches: e.g. `radian per second`	`radian per second squared` want to keep megaHertz	megahertz	and angstrom	ångström	so try with keeping first regex match yes it works to do that removed second regex match.



237 unmapped terms to figure out how to get or are missing from OM, 164 X based unit terms
figure out if it's because they don't exist in OM, or if my script is still missing some things.


e.g., UO:0000068	molal should map to http://www.ontology-of-units-of-measure.org/resource/om-2/Molality molality. Can manually check these and know what synonyms to add to UO e.g., `molality` to `molal`. Then hopefully they'll get captured in the mapping. Some terms aren't in OM e.g., UO:0000207	`milliliter per liter` or `millilitre per litre`

More examples UO:0000062	molar not mapping to OM because they have spell it `molair` http://www.ontology-of-units-of-measure.org/resource/om-2/molair which looks to be dutch for molar but OM has this spelling for both english and dutch labels. Can probably catch these with hamming distances but might want to produce a report of assignments caught with hamming distances so that we can manually review them or make a bug report for OM.  
see https://github.com/kaiiam/biosys-analytics/blob/master/assignments/13-hamm/hamm.py for hamming dist. 
