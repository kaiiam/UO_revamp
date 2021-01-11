# Setup

Semi-manually made a list of all OM base units see `UO_revamp/scripted_term_creation/cross_unit_prefix/OM_unique_units.txt`. From that file containing both base and derived unit cobos, I saved the base terms here to  `om_base_full.csv`

Took the mapping output from `UO_revamp/mapping/uo_to_om/output_uo_to_om_mapping.csv`, verified it manually and saved it to [this google sheet](https://docs.google.com/spreadsheets/d/1JSGDVrF7hfGIgjUYqO40wUhSCUIp5SEDXGa5yMKQCtA/edit?usp=sharing) see the sheet `verified_uo_om_mapping.csv`. Next I used that as the input file here to check against the list of OM base terms `om_base_full.csv`.

Finally this script generates the `unmapped_om_base.csv` list of unmapped OM base terms. Which is also saved to the same [google sheet](https://docs.google.com/spreadsheets/d/1JSGDVrF7hfGIgjUYqO40wUhSCUIp5SEDXGa5yMKQCtA/edit?usp=sharing).

# Use

Using the ist of unmapped base terms, find or create an appropriate match in UO. Then add that matched mapping to `verified_uo_om_mapping.csv` google sheet. Redownload it as the csv, and re-run the `mapping_uo_to_om.py` script. Check the `unmapped_om_base.csv` now has less terms, and re-upload it to the google sheet. Repeat until all missing base OM terms are completed.

Added the suggested `UO_revamp/mapping/uo_to_om/suggestions_uo_to_om.csv` mappings to `verified_uo_om_mapping.csv`.


Made an additonal sheet `missassigned_uo` for incorrectly suggested unit mappings to be manually mapped and added to the `verified_uo_om_mapping.csv`. 

Note this is only the base OM terms, the compound terms are still in `UO_revamp/scripted_term_creation/cross_unit_prefix/OM_unique_units.txt` to be dealt with when making unit combos.

Once completed, we can rerun the whole pipeline again to make sure that we're not missing any desired OM terms.
