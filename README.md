# Automated testbed
This directory contains all the source files related to Automated testbed project.


Automated testbed project is a set of scripts for automation of setting up of testbed, installation of application (Hadoop), configuring analytics application and collection of performance metrics.


It consists of three key features,

App: This is a Splunk custom application for monitoring the performance metrics collected from switches, servers, virtual machines and application. This directory contains the custom Splunk application.


Test infrastructure: Test infrastructure consists of switches, baremetal servers, virtual machines and the application or the workload. Ansible and cobbler scripts are under ansible, hadoop_installation and cobbler directories for setting up of a Hadoop based application.


Performance metrics collection: Collectd directory contains configuration for performance metrics collection from Linux, switches and Hadoop. This also contains configuration for transferring the metrics to a Splunk server.

User guide:  User guide is located under docs directory.

How to use:

Step 1: Setup infrastructure specifically, switches, server (with Linux OS), VM with Splunk, A VM for running Ansible and collector.
Step 2: Setup Hadoop by using ansible scripts
Step 3: Build Splunk app by running build.py
Step 4: Install Splunk app on Splunk server and restart Splunk.
Step 5: Configure collectd-client.conf with collectd server/ Splunk server address and update these on the nodes from where metrics are collected.
Step 6: Add a Splunk Job from application dashboard.
