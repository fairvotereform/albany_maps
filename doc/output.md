
Maps produced using 2019 census block groups.

## stats file (map_stats.csv)

One row per map.

Currently, there are only 2 district maps. For naming purposes, LD refers to large district and SD refers to small district.

Column descriptions:
* **map_id** - Number assigned to maps in order of generation.
* **jurisdiction_cvap_total_count** - Total CVAP estimate for jurisdiction. Total sum of all CVAP race/ethnicity estimate values in all block groups.
* **[LD|SD]_cvap_total_count** - CVAP estimate for district. Sum of all block group CVAP race/ethnicity estimate values in the district.
* **[LD|SD]_cvap_total_perc** - CVAP percent estimate for district.
* **[LD|SD]\_cvap\_[race/ethnicity]_[Alone/Combined]_perc** - CVAP rate/ethnicity estimates as a percentage of district total CVAP. The possible race/ethnicities reported in the stats file are: 
    * White
    * Black or African American
    * Asian 
    * Hispanic or Latino
    * American Indian or Alaska Native
    * Native Hawaiin or Other Pacific Islander
    * Remaining

    These categories are aggregated version of the categories present in the ACS data. The ACS race/ethnicity data at the block group level contains 11 categories: 
    * White 
    * Black or African American
    * Asian 
    * Hispanic or Latino
    * American Indian or Alaska Native
    * Native Hawaiin or Other Pacific Islander
    * Black or African American and White
    * Asian and White
    * American Indian or Alaska Native and White
    * American Indian or Alaska Native and Black or African American
    * Remainder of Two or More Race Responses
    
    Because of the presence of multi-group categories (e.x. Asian and White), these ACS categories have been aggregated in two ways, "Alone" aggregation and "Combined" aggregation. In "Alone" aggregation, all multi-groups are aggregated into the Remaining category. In the "Combined" aggregation, multi-groups containing the category "White" are grouped in with the non-White component of the multi-group (e.x. the estimate for Asian = Asian + Asian and White). In this aggregation, the only categories left allocated to the "Remaining" category are "American Indian or Alaska Native and Black or African American" and "Remainder of Two or More Race Responses".
    
* **[LD|SD]\_housing_[own/rent]_perc** - Percentage of renters and owners in the district.
* **[LD|SD]\_income_bucket_at_quota** - The income range necessary to achieve a low income coalition big enough to reach the election quota for the district, assuming all people below and including this income range vote as a block.
* **SD_quadrant** - a rough estimate of which quadrant of the city the small district is located within. Possible values are: SW, SE, NW, NE.
* **[LD|SD]_geoids** - concatenated block group geoids.


## individual partition plots (*_map_stats.png)

* **top left** - District population percentage estimates using CVAP data.
* **top middle** - District map.
* **top right** - District renter percentage estimates.
* **middle left** - Large district race/ethinicity distribution, "Alone" aggregation.
* **middle middle** - Large district race/ethinicity distribution, "Combined" aggregation.
* **middle right** - District estimated income distribution.
* **bottom left** - Small district race/ethinicity distribution, "Alone" aggregation.
* **bottom middle** - Small district race/ethinicity distribution, "Combined" aggregation.
* **bottom right** - District estimate cumulative income distribtion.

## all partition summary plots (map_summary.png)

This plot shows the distribution of values presented in the individual partition plots across all made maps. The only new plot is the quadrant plot, which shows the distribution of quadrants the small district was located within across all maps.