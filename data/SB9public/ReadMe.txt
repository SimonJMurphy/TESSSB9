Description of SB9

In all cases, "|" is the field separator.

Main.dta
  Field #         Description
     1            System Number (SB8: <=1469)
     2            1900.0 coordinates (for backward compatibility with SB8)
     3            2000.0 coordinates
     4            Component
     5            Magnitude of component 1
     6            Filter component 1
     7            Magnitude of component 2
     8            Filter component 2
     9            Spectral type component 1
    10            Spectral type component 2


Orbits.dta
  Field #         Description
     1            System number
     2            Orbit number for that system
     3            Period (d)
     4            error on P (d)
     5            Periastron time (JD-2400000)
     6            error on Periastron time
     7            Flag on periastron time
     8            eccentricity
     9            error on eccentricity
    10            argument of periastron (deg)
    11            error on omega
    12            K1 (km/s)
    13            error on K1 (km/s)    
    14            K2 (km/s)
    15            error on K2 (km/s)
    16            systemic velocity (km/s)
    17            error on V0 (km/s)
    18            rms RV1 (km/s)
    19            rms RV2 (km/s)
    20            #RV1
    21            #RV2
    22            Grade (0:poor, 5: definitive)
    23            Bibcode
    24            Contributor
    25            Accessibility
    26            Reference adopted for the times (JD or MJD)

Alias.dta
  Field #         Description
     1            System number
     2            Catalog name
     3            ID in that catalog


Reference:
Any user of SB9 is encouraged to acknowledge the catalogue with a 
reference to
 "SB9: The ninth catalogue of spectroscopic binary orbits", 
 Pourbaix D., Tokovinin A.A., Batten A.H., Fekel F.C., Hartkopf W.I., 
 Levato H., Morrell N.I., Torres G., Udry S., 2004, 
 Astronomy and Astrophysics, 424, 727-732.
