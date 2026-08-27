---
layout: data_jp
title: "Data"
description: "C-PROOF Glider Data"
header-img: "img/MikeSaanich19.jpg"
---

If you use C-PROOF data, please cite: <i>Klymak, J., & Ross, T. (2025). C-PROOF Underwater Glider Deployment Datasets [Data set]. Canadian-Pacific Robotic Ocean Observing Facility. doi:<a href="https://doi.org/10.82534/44DS-K310">10.82534/44DS-K310</a></i>.

## Data Description

Raw data from the gliders is available for most [deployments](/deployments). We further provide CF-compliant NetCDF files as either:

- Timeseries: high-resolution data aligned with the clock on the CTD sensor.
- Gridded: 1-m vertical grid, with one column per up or down profile.

The data is  available at different levels of processing:

- Realtime: Subset of data transmitted via Iridium while the glider is in mission, with automated processing steps and QA/QC applied.
- Delayed: Full dataset collected by the glider and recovered post-mission, with all processing steps and QA/QC applied.
- Corrected: Some data has corrections applied to the CTD data and/or the oxygen data to correct for thermal lag and sensor drifts.
  - A general description of the corrections applied is available in the [data processing report](https://cproof.uvic.ca/gliderdata/deployments/reports/), and each specific deployment has a detailed report in the `reports/` subfolder.

## Where were the gliders, and when?

See [SSH plots new]({{ site.baseurl }}/gliderdata/deployments/sshplotsnew) for SSH and glider track plots for each day of C-PROOF.

## Data access:

### By individual deployment:

See [Deployments]({{ site.baseurl }}/deployments/index.html) to view and download data and figures for individual glider missions.

### Gridded data via THREDDS:

Data binned in depth and time are available via our [THREDDS server](https://cproof.uvic.ca/thredds/).  The THREDDS server allows partial downloading of data sets using the ODAP protocol.  Using python xarray something like `ds=xr.open_dataset('https://cproof.uvic.ca/thredds/dodsC/gridsCalvert/dfo-hal1002-20220914_grid_delayed.nc')` should give data access without having to download and store the dataset locally.  You can [do a similar thing in Matlab](https://www.mathworks.com/help/matlab/import_export/reading-netcdf-data-directly-from-remote-locations.html#mw_b2b95cb8-d257-4289-84a9-0756967e3ad4) and in [R](https://rdrr.io/cran/RNetCDF/man/open.nc.html) or any other library that supports [OPeNDAP](https://www.earthdata.nasa.gov/engage/open-data-services-and-software/api/opendap).

### Direct download using wget.

To download all the mission data, type the command

```
wget -N --directory-prefix=outdir \
   --input-file=https://cproof.uvic.ca/gliderdata/deployments/mission_all.txt
```

To download all the data by glider line or by platform, replace [`mission_all.txt`](https://cproof.uvic.ca/gliderdata/deployments/mission_all.txt) with one of the following:

- Glider lines
  - [`LineP.txt`](https://cproof.uvic.ca/gliderdata/deployments/LineP.txt)
  - [`CalvertLine.txt`](https://cproof.uvic.ca/gliderdata/deployments/CalvertLine.txt)
  - [`Southern.txt`](https://cproof.uvic.ca/gliderdata/deployments/Southern.txt)

### ERDAP server:

Our data is available on the [IOOS ERDAP server](https://gliders.ioos.us/erddap/index.html), available by searching `C-PROOF`.  (It is apparently somewhere on the Coriolis server as well, but not easy to find).


## How to Cite

When publishing C-PROOF ocean glider data, please cite:
<i>Klymak, J., & Ross, T. (2025). C-PROOF Underwater Glider Deployment Datasets [Data set]. Canadian-Pacific Robotic Ocean Observing Facility. doi:<a href="https://doi.org/10.82534/44DS-K310">10.82534/44DS-K310</a></i>
If you are using C-PROOF data, please contact Dr. Jody Klymak (jklymak@uvic.ca) so we can add a citation to your publication.
