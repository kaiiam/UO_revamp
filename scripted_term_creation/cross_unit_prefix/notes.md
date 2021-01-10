From the [SI-Brochure-9.pdf](https://www.bipm.org/utils/common/pdf/si-brochure/SI-Brochure-9.pdf)

https://www.bipm.org/en/publications/si-brochure/
https://www.bipm.org/utils/common/pdf/si-brochure/SI-Brochure-9.pdf

have 22 named SI units with their own symbols:

radian,steradian,hertz,newton,pascal,joule,watt,coulomb,volt,farad,ohm,siemens,weber,tesla,henry,degree Celcius,lumen,lux,becquerel,gray,sievert


For prefixes, note kibi gibi etc are recommended for powers of 2.



page `167` for Derived units appendix

page `172` for Resolution 6 appendix



`in_csv/`

named_SI_units.csv -> [named SI units](https://en.wikipedia.org/wiki/Metric_units)

non_SI_units_mentioned_in_SI.csv -> [SI mentioned non SI](https://en.wikipedia.org/wiki/Non-SI_units_mentioned_in_the_SI)

SI_base_units.csv -> [base units from SI](https://en.wikipedia.org/wiki/International_System_of_Units)

prefix.csv -> [SI metric prefixes](https://en.wikipedia.org/wiki/Metric_prefix)

units_to_cross.csv combo of above (what was in UO) that can have metric prefies AFAIK. Missing some not currently in UO, e.g. `bel`.



For script see `~/Desktop/scratch/CDNO/gen_NCF_robot_template/gen_NCF_robot_template_split/gen_NCF_robot_template_split.py` as basis



# meeting with James:


can use robot diff to make sure the OBO file is good.

James thinks that changing the EQ axioms e.g., anything away from milliampere from

`'ampere based unit'
 and (has_prefix some milli)`

 is ground for deprication as someone maybe using that EQ in their system. I think that depricating the old ID is more likely to cause issues for existing users.

 Could like to python systems which do unit conversions e.g. pint. James has a list of these.
