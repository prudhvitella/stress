# stress
Docker stress container

You can set and view CPU/Memory over a webpage.

To run:
* docker run -d -p 5000:5000 prudhvitella/stress

To use:
* /stats - See current CPU/Memory usage
* /cpu/<Percentage> - Sets the amount of CPU usage. Any percent over 100 will create multiple processes. e.g. /cpu/120 will  create 1 process with 100% and another with 20% usage
* /mem/<MB> - Set memory to use. e.g. /mem/1024 to use 1024MB of memory
