# Thoughts:

### reasoner

clearly the current uo.owl hasn't been run through a reasoner.

### unit of axioms:

PATO follows a pattern with subclass axioms like

```
is_unit_of only
(PATO_0000992) <- viscosity
```

I like the idea of assigning units to a pato hierarchy but I can imagine Chris would be against using qualifiers like only.

### prefix and equivalent classes:


UO has this structure of `x based unit classes` E.g. `gram based unit` with combinatorial classes using these classes in an equivalence axiom pattern. Some UO classes also combine this with prefixes within EQ axioms, e.g. `nanogram` which has the EQ:


```
'gram based unit' and (has_prefix some nano)
```


This prefix pattern breaks down, however, when we get to compound units: where some classes do and don't follow this pattern:

`nanogram per microliter` has EQ: `{'nanogram per microliter'}`

`nanogram per milliliter` has 2 EQs (BAD practice!): `{'nanogram per milliliter'}` and `'gram per milliliter based unit' and (has_prefix some nano)`



### Groovy baby

The groovy script `unitsconverter.groovy` takes the edit file `unit.obo` and generates the other files. unfortunately this makes for some wired stuff in the owl file, including the equivalence classes. Although I appreciate the groovy unit converter script, robot is a better way to convert between OBO and owl. Especially since the current workflow moving from  `unit.obo` to `uo.owl` misses quite alot.


It changes definitions to comments, and removes the following: ID in curie form, has_obo_namespace, comment, hasRelatedSynonym, created_by, creation_date, in_subset, has_alternative_id.


Using robot export I can get almost everything from `unit.obo` except the `database_cross_references` on the `definitions`. Using the results of robot export on the `unit.obo` and `uo.owl` I can join them together to get the hasDbXrefs. However, I should ask James if this is possibly via Robot export.


# Questions

1) What's up with the EQ's like `{mole}` in `mole` UO:0000013? -> groovy baby!

2) If we were to have an EQ and follow a Design Pattern what should it include?




***
# Ideas for breaking down UO into Robot Modules

### Idea 1 by it's top level unit classes:  

```
acceleration unit
angle unit
angular acceleration unit
angular velocity unit
area unit
base unit
catalytic activity unit
concentration unit
conduction unit
density unit
dimensionless unit
electric charge
electric current unit
electric field strength unit
electric potential difference unit
energy unit
force unit
frequency unit
information unit
length unit
light unit
magnetic flux density unit
magnetic flux unit
mass unit
momentum unit
power unit
pressure unit
radiation unit
rate unit
speed/velocity unit
substance unit
surface tension unit
temperature unit
time unit
turbidity unit
viscosity unit
volume unit
volumetric flow rate unit
```


There are 38 of these so shouldn't be one template each, need to break this down furthur.


### Idea 2 by it's PATO part of relations

UO has the following is unit of relations to PATO classes:

```
speed	PATO:0000008 -> physical quality
concentration of	PATO:0000033 -> molecular quality
frequency	PATO:0000044 -> process quality
weight	PATO:0000128 -> physical quality
orientation	PATO:0000133 -> physical quality
time	PATO:0000165 -> physical quality
viscosity	PATO:0000992 -> physical quality
mass density	PATO:0001019 -> physical quality
energy	PATO:0001021 -> physical quality
impulse	PATO:0001022 -> physical quality
momentum	PATO:0001023 -> physical quality
power	PATO:0001024 -> physical quality
work	PATO:0001026 -> physical quality
acceleration	PATO:0001028 -> physical quality
force	PATO:0001035 -> physical quality
luminous flux	PATO:0001296 -> physical quality
radiation emitting quality	PATO:0001299 -> physical quality
duration	PATO:0001309 -> process quality
angular acceleration	PATO:0001350 -> physical quality
area density	PATO:0001351 -> physical quality
linear density	PATO:0001352 -> physical quality
volumetric density	PATO:0001353 -> physical quality
angular velocity	PATO:0001413 -> physical quality
catalytic activity	PATO:0001414 -> physical quality
medium acidity	PATO:0001428 -> molecular quality
surface tension	PATO:0001461 -> physical quality
electric potential	PATO:0001464  -> physical quality
sound amplitude	PATO:0001521 -> process quality
flow rate	PATO:0001574 -> physical quality
catalytic (activity) concentration	PATO:0001674 -> molecular quality
molar volume	PATO:0001680 -> morphology
molar mass	PATO:0001681 -> physical quality
magnetism	PATO:0001682 -> physical quality
1-D extent	PATO:0001708 -> morphology
2-D extent	PATO:0001709 -> morphology
3-D extent	PATO:0001710 -> morphology
radiation emitting intensity quality	PATO:0001717 -> physical quality
luminance	PATO:0001718 -> physical quality
activity (of a radionuclide)	PATO:0001740  -> physical quality
radiation exposure	PATO:0001744 -> physical quality
radiation absorbed dose	PATO:0001745  -> physical quality
radiation equivalent dose	PATO:0001746  -> physical quality
radiation effective dose	PATO:0001747  -> physical quality
heat conductivity	PATO:0001756  -> physical quality
electrical conductivity	PATO:0001757 -> physical quality
mass	PATO:0000125  -> physical quality
temperature	PATO:0000146  -> physical quality
pressure	PATO:0001025 -> physical quality
```

38 physical quality
4 morphology
3 molecular quality
3 process quality

Doing this will create 4 groups with an uneven distribution but it's one idea to break it up.

This could be confusing we get stuff like `area unit` corresponds to `2-D extent` which is a PATO:`morphology` def~A quality of a single physical entity inhering in the bearer by virtue of the bearer's size or shape or structure. I guess this makes sense but it's probably still confusing to look for areas under morphology for non-biologists.


### Idea 3

3 modules: 1) physical object quality 2) process quality 3) prefix

### Idea 4

Break them down based on compound and base units, the idea being that we can derive the Compound units from combos of the base units. Or maybe just have one table for all of it? Plus a separate one for prefixes?

**Base Unit template** -> named units?

'acceleration unit'
'angle unit'
'area unit'
'base unit'
'electric charge' (only C)
'electric current unit'
'electric potential difference unit' (volts)
'force unit' (N named unit even though it has constituent parts)
'length unit'
'magnetic flux density unit' (Telsa)
'power unit'
'pressure unit' (all named but can break down)
'substance unit' (mole family)
'temperature unit'
'time unit'
'turbidity unit'

**Compound Unit template**

'angular acceleration unit'
'angular velocity unit'
'catalytic activity unit' -> could go either way it's rates but in one unit
'concentration unit'
'conduction unit' -> includes some single units like siemens but mostly compound
'density unit'
'electric field strength unit'
'magnetic flux unit'
'momentum unit'
'rate unit'
'speed/velocity unit'
'surface tension unit'
'volumetric flow rate unit'


**Contains both Compound and Base**
'dimensionless unit' -> some compound some are not e.g. parts per x, ratio. vs cfu. Could break it up?
'energy unit'
'frequency unit'
'information unit' (mostly base but some are compounds)
'light unit'
'mass unit' -> all but molar mass are single units
'radiation unit' all but activity (of a radionuclide) unit are named.
'viscosity unit'
'volume unit' (mostly base except molar volume unit, and specific volume unit)






#QUDT

Unlike UO, all QUDT units are instances, e.g. `Microgram Per Litre`. Unit instances have OPs relating to the QUDT model e.g., `has quantity kind` `mass density`, and DPs like `conversion multiplier` `1.0E-6`. Doesn't appear to have ways of asserting numerator or denominator like OM/OBOE. Importantly QUDT links to UCUM codes as APs, e.g. `ucum Code` `ug/L`.





# OM

All OM units are instances like QUDT.

OM has object property assertions for numerators and denominators, e.g. `centimole per litre` has the OP assertions: `has denominator` `litre`, and `has numerator` `centimole`, and `has dimension` `amount of substance concentration dimension`.

The latter is also an instance and it has data property assertions like `has SI mass dimension exponent`. That interesting, we could easily map to the unit instances but we'd louse the whole data model with OP and DP. Cool stuff should learn more about what this can do.


# OBOE's units

Like UO all units are classes not instances. Has upper level classes for 'Base Unit', 'Composite Unit', 'Derived Unit'.

`liter` has SC axiom:

```
standardFor only
    (Measurement
     and ('of characteristic' only Volume))`
```
works within their larger data model analogous to UO's specifying `is_unit_of only X PATO term`.

Composite units, e.g. `MicrogramPerLiter` specifies numerator and denominator via the following SC axioms:

```
'has unit' some Microgram
```

```
'has unit' some
    ('Derived Unit'
     and ('has unit' only Liter)
     and (hasPower value -1))
```




# What should UO 2.0 include?


Do we want to maintain UO's use of EQ axioms? IF so can we stabalize this into a well defined Design pattern? Perhaps with scripted ways to generate the robot tempates for it? What else should such a Design Pattern include?

Do we want to assert numerator and denominator like OM/OBOE?

Definitely want to map to UCUM codes, and iri's from QUDT (possibly also OM)


I like the idea of creating/booting up a new ontology, follwing the lines of how UO works based on 1) filling out the base units (UO_0000045), then crossing them with prefixes `mili`, `micro` `centi`, etc to create an X based unit terms  (e.g. meter based unit, with subclass millimeter). Then these can be further used to make combinatorial units. E.g. `millimeters per day`.

Need to find missing top level X unit classes in UO, e.g. volumetric flux units, or other classes of units needed for BCODMO e.g. `centimeters/kiloyear`, `micromoles/liter/day`




# steps


### Identify missing base units

E.g. `atmosphere`

E.g. `kilogram` is there but `gram` isn't. Do we want to have the base units there? or perhaps multi-inheritance there and to the appropriate x based unit term?

Under `turbidity unit` theres a missing one have FNU but there's a separate on see PM.

### Identify essential X base unit hierarchies to fix out in a first pass:

E.g. the `meter based unit` hierarchy

`gram based unit`, `molal based unit`, `molar based unit`


### Identify inconsistencies/mistakes  

E.g. `micromole per litre` and `micromolar` should be the same thing. The former is under the `unit of molality` hierarchy which defined as per kilogram of solvent, so it seems incorrect.

E.g. Running the ELK reasoner, `milligram per milliliter` and `milligram per liter` are inferred to be equivalent. This is because both of them have the equivalence axiom:

```
'gram per liter based unit'
 and (has_prefix some milli)
```
So clearly this equivalence axiom pattern breaks down with compound units `mg/L` being called equivalent to `mg/mL`. Do we want to expand the above EQ class expression out to have denominator and numerator, perhaps each with a prefix? What about for more complex units with multiple atomic parts in the num/denom e.g. `uE/cm^2/sec`. Check this one as the Eignsteins aren't a unit along in UO only with the combo.

### Fill out prefix combos with base units

we have watt UO_0000114, but not megawatt kilowatt etc. DP should be automated to cross these with prefixes to generate input for robot templates.

Another example we currently have:

```
'electric field strength unit'
  'volt per meter based unit'
    'volt per meter'
```

But it's bad practice to have the middle class like that if there aren't more intermediate nodes, so we could auto fill out all the `'volt per meter based unit'` children (e.g. volt per cm, volt per nm etc) drawing these from the completed `meter based unit` hierarchy. Might as well do that with all metric prefixes.

Similar story for `square centimeter based unit`, `square micrometer based unit` etc. Makes for a horribly gangly hierarchy.



### clean up existing X unit hierarchies

e.g. in the `rate unit` `UO_0000280` hierarchy there's seems to be alot to clean up. E.g. we have two mid level classes `count per molar second based unit` and `count per nanomolar second based unit` with EQ's below them `count per molar second` and `count per nanomolar second` respectively. I'm confused about these units what this is for? Assuming their real, would it not make more sense to have a mid level class like `count per molar time` which would have under it both `count per molar second` and `count per nanomolar second`?







### Map to QUDT maybe OM

see #Mapping






# Mapping:

UCUM codes (currently only in QUDT) would be a great way to map between the units ontologies. OM doesn't use UCUM codes, however, OM has similar symbols e.g. `μg/l` but since it's case sensitive, unfortunately these won't quite correspond automatically. I'm thinking we could do a first pass at mapping UO with QUDT/UCUM by string matching labels e.g. QUDT: `Ampere` with UO: `ampere`, (might need to do this semi-manually). Then for matches of UO to QUDT, assign the UO term the appropriate UCUM codes from QUDT, as well as QUDT iri's like `http://qudt.org/vocab/unit/A` (for ampere).

For the label matching maybe we could use a python script which does some stemming.

To map UO out to the others, we'd run through all UO classes, with their labels stemmed down to all lowercase maybe if we could use SYNONYMS too and do use them as well to match. Then we'd also do the same for the other ontologies. Then string match or maybe even use something more sophisticated like hamming distance matches as not to louse things like `liter vs litre`. There is an example like this from Kens class, see if it's useful here. This could then generate putative mappings between UO and the others (QUDT and possibly OM). Then maybe manually check those mappins to make sure it's ok, manually remove anything fishy, then, assign to UO any new information found, e.g. UCUM codes from QUDT, links to QUDT/OM iris etc.






#
