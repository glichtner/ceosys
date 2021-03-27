CEO-sys AP5 automatic guideline adherence evaluator
######################################################

<img src="docs/img/logo_ceosys.jpg" alt="CEOsys" width="20%" />
<img src="docs/img/logo_num.jpg" alt="NUM" width="20%" />


Introduction
============
Development of a software-based automated evaluation of the adherence to clinical guidelines in the context of the
[CEO-sys - COVID-19 Evidenz-Ökosystems zur Verbesserung von Wissensmanagement und -translation](https://covid-evidenz.de/).

Quickstart
==========

1. Clone repository
   ..code-block shell
   git clone https://github.com/glichtner/ceosys.git
   ```

2. Create data directory and copy a data sample (not included in this repository)
   ``` shell
   cd ceosys/
   mkdir data/
   cp <path-to-example-file> data/sample_data_shuffle.csv.gz
   ```

3. Build docker containers
   ``` shell
   docker-compose build
   ```

4. Run containers
   ``` shell
   docker-compose up
   ```
5. Visit the dashboard under http://localhost:5000/
