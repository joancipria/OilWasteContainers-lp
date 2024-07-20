```bash
sudo apt-get install gdal-bin libgdal-dev libjsoncpp-dev
```

```bash
python setup_population_calculator.py build_ext --inplace
```

```bash
export CPLUS_INCLUDE_PATH=/usr/include/gdal:$CPLUS_INCLUDE_PATH
export LIBRARY_PATH=/usr/lib:$LIBRARY_PATH
```