## install dep

```bash
git clone https://github.com/eclipse/paho.mqtt.c.git
cd paho.mqtt.c
mkdir build
cd build
cmake ..
make
sudo make install

export LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH}
```
# build bps
```bash
cd bps
mkdir build
cmake ..
make

```
