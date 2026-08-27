---
layout: project_jp
title: "Observatory"
description: "C-PROOF Observatory"
header-img: "img/MikeSaanich19.jpg"
---



### Glider observatory

The C-PROOF glider missions are designed to better understand the structure of ocean properties offshore of British Columbia's coast, and how those properties are mixed between coastal water and offshore water.

Currently, we maintain three lines as regularly as funding, time, and equipment will allow.  *Line P* is a historic line that goes from coastal BC to the middle of the Alaska Gyre at "Station P" (50 N, 145 W).  The *Calvert Line* runs from Calvert Island in Queen Charlotte Sound offshore, sometimes as far west as Station P16.  The most recently added line is the *Southern Line*, which goes offshore from Tofino, approximately perpendicular to the coast.

There are a number of other missions that have taken place, including a partnership with Council of Haida Nation and Gwaii Haanas, including measurements in the Gwaii Haanas National Marine Conservation Area Reserve and Haida Heritage Site as well as other regions of cultural significance. We have also had a few missions that run along the coast, either for logistical reasons, or in order to follow the SWOT altimeter line.

<div class="containerjp">
<figure>
<img src="/img/cprooflines.png" alt="C-PROOF Schematic">
<figcaption style="text-align:center;font-style: italic;font-size: 16px;">C-PROOF glider tracks (excluding an Arctic mission).  We operate on three main lines, "Line P", "Calvert Line" and "Southern Line". Lines are colored by date, with red being more recent.</figcaption>
</figure>
</div>

Deployments started in 2019, but really ramped up in late 2022 as most of the glider fleet was acquired.  Since that time, we have often had three gliders in the water at all times.

<div class="containerjp">
<figure>
<img src="/img/CPROOFDeploy.png" alt="C-PROOF Schematic">
<figcaption style="text-align:center;font-style: italic;font-size: 16px;">
Deployment times versus longitude, with colours representing latitude (blue further north, red further south).
</figcaption>
</figure>
</div>

### Glider line vocabulary

Download <a href="./cproof_line_vocab.yml">cproof_line_vocab.yml</a> to see the full list of glider lines and their waypoints.

<div class="containerjp">
<figure>
<img src="/img/cprooflines_defs.png" alt="C-PROOF Lines">
<figcaption style="text-align:center;font-style: italic;font-size: 16px;">C-PROOF line vocabulary definitions.</figcaption>
</figure>
</div>


{% assign lines = site.data.cproof_line_vocab.lines %}
{% for l in lines %}
  {% assign line = l[1] %}
  <h4>{{ l[0] }} </h4>
  <em>{{ line.long_name }}:</em> {{ line.description }}
  <table>
  <thead>
    <tr>
      <th>Station</th>
      <th>Latitude</th>
      <th>Longitude</th>
    </tr>
  </thead>
  <tbody>
    {% for wp in line.waypoints %}
    <tr>
      <td>{{ wp.station }}</td>
      <td>{{ wp.lat }}</td>
      <td>{{ wp.lon }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
<br>
<hr>

{% endfor %}
