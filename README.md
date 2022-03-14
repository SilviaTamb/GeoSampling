# GeoSampling

Python package for sampling geographical polygons, developed as Master thesis in Data Science at University of Milano-Bicocca. Comments and docstrings are in italian.
 
This package assumes data in this form:
 
- N+1 rows, indexed as 0, 1,...N, and every row is a point.
- Row 0 is equal to row N, and the last 'true' point is row N-1;
- Points are ordered: point at index i and point at index i+1 are adjacent;
- Order of points is invariant with respect to a cyclic permutation: ABCD is equivalent to BCDA, CDAB, DABC;
- Two columns: a 'Latitude' column with a floating point inside, a 'Longitude' column with a floating point inside.
- North Latitude is positive, East Longitude is positive.

This package has been tested on confidential data. Data will not be shared.
