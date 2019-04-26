*This program analyzes possible appearance of train accidents*

**Design decisions**  
Length of way is an integer. There is no circle motion, - there are single  
bidirectional tracks between stations. But train drivers are hooligans and  
sometimes reverse motion could be given. Station and train are presented as  
a point. Every station has a capacity - quantity of trains in that station
in the moment.

Name of station should consist of letters. Every section of railway has name  
that consist of start name point and end name point, sorted in lexicographical  
order. There is no waiting time for trains, so, for example station.arrival =  
station.departure.
Traffic Service has a railway configuration and makes the overall sections
timetable and stations timing.  
*This is not work timetable, but timetable for routes analysis*  
Sections timetable consist of shedules for every section of railway.

**Traffic shedule of way section AB (A-B)**  

Item | Train number | A.departure | B.arrival
------------ | ------------- | ------------- | -------------
1 | 256 | t1 | t2 |
2 | 128 | t3 | t4 |
3 | 64  | t5 | t6 |

###### Usage example  
`python3 railway.py --config /usr/local/etc/railway_config.conf --routes /usr/local/etc/routes.conf`

*By default script takes conf files from current directory*  
*Test version python3.7*  
