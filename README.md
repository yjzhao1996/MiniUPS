# ** UPS server **
This is a server for UPS. It can connect to a world or init a world. It will listen on port 8888 for an Amazon server to connect. It will tell Amazon which world to connect.
## ** Code **
In directory web-app, /src contains all server code, and others are website code. You can change test_ups.py to specify the address of the world to connect and how many trucks to initiate.
## ** Run **
To start this application, run world-docker first. Then under UPS-docker, run:
   ** sudo docker-compose build **
   ** sudo docker-compose up **
