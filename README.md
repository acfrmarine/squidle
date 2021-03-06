
NOTE: THIS CODE IS OLD, OUT OF DATE AND NO LONGER MAINTAINED. THERE IS A NEW AND IMPROVED VERSION OF A COMPLETELY REDESIGNED SYSTEM HOSTED HERE: http://squidle.greybits.com.au/
=======================================================


Squidle
======

In recent years, ecologists and biologists have increasingly relied on digital video and image-based methods to examine and monitor marine habitats. These data streams are routinely collected by underwater platforms including Baited Remote Underwater Video Systems (BRUVS), Autonomous Underwater Vehicles (AUV), Remotely Operated Vehicles (ROV) and Underwater Towed Video (UTV) systems. Transforming visual data into quantitative information for science and policy decisions, requires substantial effort by human experts. However, there is currently no standardised approach for the cataloguing, annotation, classification and analysis of this imagery. Different research groups tend to handle the collected data in different ways, using different sampling techniques, different annotation tools and even referring to the same taxa by different names. This makes comparison across disparate sites difficult, resulting in little data re-use amongst groups. It also presents a significant barrier to asking ‘big picture’ questions that could be answered if quantitative data was available in a consistent format in a centralized repository.

Squidle is a web-based framework that aims to facilitate the exploration, management and annotation of marine imagery. We are working closely with members of the marine science community to create a streamlined, user-friendly interface that integrates sophisticated map-based data management tools with an advanced annotation system. Users are able to quickly select data using advanced queries (eg: depth, altitude, date, deployment or bounding box), which they can then subsample and annotate using a selection of standardised, agreed upon methods. The interface will be extended to incorporate machine learning tools for automated clustering and supervised classification, which will serve to streamline and enhance data exploration, subsetting and annotation. Data import & export tools will make it easier to import existing labels from commonly used annotation programs (eg CPCe), and also provide reporting tools for summaries and statistics. The project aims to deliver a reliable, advanced and easy-to-use web-based framework that facilitates direct access to survey data in an effort to reduce the latency between collecting and interpreting marine imagery.

Installation
============

In order to install squidle, follow these instructions.  This should download the archive from github, install required depencies and setup the postgres database and geoserver.

> git clone https://github.com/acfrmarine/squidle.git
> cd squidle
> ./scripts/install-scripts/install

This setup has been tested on Ubuntu 12.04.

For those wishing to use the squidle interface, we maintain a server that includes the IMOS AUV Imagery here:

http://squidle.acfr.usyd.edu.au



