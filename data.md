---
layout: data_jp
title: "Data"
description: "C-PROOF Mission"
header-img: "img/MikeSaanich19.jpg"
---

<script>
//https://stackoverflow.com/questions/45615998/on-click-copy-to-clipboard/45616055
function copyToClipboard(element) {
  var $temp = $("<input>");
  $("body").append($temp);
  $temp.val($(element).text()).select();
  document.execCommand("copy");
  $temp.remove();
}
</script>

<style>
/*https://stackoverflow.com/questions/7117073/add-a-tooltip-to-a-div*/
[data-tooltip]:before {
    content: attr(data-tooltip);
    position: absolute;
    opacity: 0;
    
    /* customizable */
    transition: 0.2s;
    padding: 10px;
    color: #FFFFFF;
    border-radius: 5px;
    box-shadow: 2px 2px 1px silver;  
    font-size: 12px;
    line-height: 16px;
}
[data-tooltip]:hover:before {
    opacity: 1;
    /* customizable */
    background: #979BA0;
    margin-top: -35px;
  /*  margin-left: 60px;*/
}

[data-tooltip]:not([data-tooltip-persistent]):before {
    pointer-events: none;
}

</style>

# Downloading Glider Data

## Setup:

You will need to install the wget package onto your system in order to retrieve the data. \
To show whether the wget package is installed on your system, type the command `wget` in a terminal window and press enter. \
If you have wget installed, the system will print `wget: missing URL`. \
Otherwise, it will print `wget command not found`.

### Install using Homebrew on macOS Sierra

<div data-tooltip="Click to copy" class="language-plaintext highlighter-rouge "><div class="highlight"><pre class="highlight"><code id="copy1" onclick="copyToClipboard('#copy1')">brew install wget
</code></pre></div></div>

### Install on Ubuntu and Debian

<div data-tooltip="Click to copy" class="language-plaintext highlighter-rouge "><div class="highlight"><pre class="highlight"><code id="copy2" onclick="copyToClipboard('#copy2')">sudo apt install wget
</code></pre></div></div>

### Install on Windows

<div data-tooltip="Click to copy" class="language-plaintext highlighter-rouge "><div class="highlight"><pre class="highlight"><code id="copy3" onclick="copyToClipboard('#copy3')"><a href="https://www.gnu.org/software/wget/">https://www.gnu.org/software/wget/</a> </code></pre></div></div>

## Get mission data:

The science files are created in `L0_timeseries` and `L0_gridfiles`. These are proper nectdf files that have metadata and attributes, and should be compliant with US-IOOS standards.

By default, the wget will download data to the directory the user is in. \
If you would like save the data in a different location use the flag  \
`--directory-prefix=outdir`  \
 where `outdir` is the name of the directory you would like to download data to. 

To download `all mission data`, type command

<div data-tooltip="Click to copy" class="language-plaintext highlighter-rouge "><div class="highlight"><pre class="highlight"><code id="copy4" onclick="copyToClipboard('#copy4')">wget -N --directory-prefix=outdir --input-file=http://cproof.uvic.ca/gliderdata/deployments/mission_all.txt
</code></pre></div></div>

To download `individual glider data`, type command 

<div data-tooltip="Click to copy" class="language-plaintext highlighter-rouge "><div class="highlight"><pre class="highlight"><code id="copy5" onclick="copyToClipboard('#copy5')">wget -N --directory-prefix=outdir --input-file=http://cproof.uvic.ca/gliderdata/deployments/dfo-[[ glidername ]].txt
</code></pre></div></div>

Ex. If you wanted all of `dfo-bb046's data`, type command 

<div data-tooltip="Click to copy" class="language-plaintext highlighter-rouge "><div class="highlight"><pre class="highlight"><code id="copy6" onclick="copyToClipboard('#copy6')">wget -N --directory-prefix=dfo-bb046 --input-file=http://cproof.uvic.ca/gliderdata/deployments/dfo-bb046.txt
</code></pre></div></div>

To download data for a particular deployment line, type command

Line P deployments

<div data-tooltip="Click to copy" class="language-plaintext highlighter-rouge "><div class="highlight"><pre class="highlight"><code id="copy7" onclick="copyToClipboard('#copy7')">wget -N --directory-prefix=linep --input-file=http://cproof.uvic.ca/gliderdata/deployments/LineP.txt
</code></pre></div></div>

Calvert Line deployments

<div data-tooltip="Click to copy" class="language-plaintext highlighter-rouge "><div class="highlight"><pre class="highlight"><code id="copy8" onclick="copyToClipboard('#copy8')">wget -N --directory-prefix=calvertline --input-file=http://cproof.uvic.ca/gliderdata/deployments/CalvertLine.txt
</code></pre></div></div>

