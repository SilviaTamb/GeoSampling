# GeoSampling

Python package for sampling geographical polygons, developed as Master thesis in Data Science at University of Milano-Bicocca. The Master thesis serves also as documentation for this package. Comments and docstrings are in italian. Please let me know if you are interested in a translation, but note that this package does not contain input checks and therefore it is (as for now) built only for personal purposes. 
 
This package assumes data in this form:
 
- N+1 rows, indexed as 0, 1,...N, and every row is a point.
- Row 0 is equal to row N, and the last 'true' point is row N-1;
- Points are ordered: point at index i and point at index i+1 are adjacent;
- Order of points is invariant with respect to a cyclic permutation: ABCD is equivalent to BCDA, CDAB, DABC;
- Two columns: a 'Latitude' column with a floating point inside, a 'Longitude' column with a floating point inside.
- North Latitude is positive, East Longitude is positive.

This package has been tested on confidential data; therefore, data and Jupyter Notebooks that contain trials and errors will not be shared.

Here is the package diagram:
![GeoSampling](https://user-images.githubusercontent.com/40537954/167361862-a8247a32-f388-47a8-9097-73a97bcaf826.jpg)
