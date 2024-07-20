#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <gdal_priv.h>
#include <ogr_geometry.h>
#include <json/json.h>
#include <vector>
#include <iostream>

// Function to create an OGRPolygon from GeoJSON coordinates
OGRPolygon* createPolygonFromCoordinates(const Json::Value& coordinates) {
    OGRPolygon* polygon = new OGRPolygon();
    OGRLinearRing ring;

    for (const auto& coord : coordinates) {
        ring.addPoint(coord[0].asDouble(), coord[1].asDouble());
    }

    ring.closeRings(); // Ensure the ring is closed
    polygon->addRing(&ring);
    return polygon;
}

// Function to parse a Polygon GeoJSON
OGRGeometry* parsePolygonGeoJSON(const Json::Value& root) {
    const Json::Value& coordinates = root["coordinates"];
    if (coordinates.isArray() && coordinates.size() > 0) {
        return createPolygonFromCoordinates(coordinates[0]);
    } else {
        std::cerr << "Invalid Polygon coordinates format." << std::endl;
        return nullptr;
    }
}

// Function to parse a MultiPolygon GeoJSON
OGRGeometryCollection* parseMultiPolygonGeoJSON(const Json::Value& root) {
    OGRGeometryCollection* multiPolygon = new OGRGeometryCollection();
    const Json::Value& coordinates = root["coordinates"];

    if (coordinates.isArray()) {
        for (const auto& polygonCoordsArray : coordinates) {
            if (polygonCoordsArray.isArray() && polygonCoordsArray.size() > 0) {
                for (const auto& polygonCoords : polygonCoordsArray) {
                    if (polygonCoords.isArray()) {
                        OGRPolygon* polygon = createPolygonFromCoordinates(polygonCoords);
                        multiPolygon->addGeometry(polygon);
                    } else {
                        std::cerr << "Invalid Polygon coordinates format in MultiPolygon." << std::endl;
                        OGRGeometryFactory::destroyGeometry(multiPolygon);
                        return nullptr;
                    }
                }
            } else {
                std::cerr << "Invalid array format in MultiPolygon coordinates." << std::endl;
                OGRGeometryFactory::destroyGeometry(multiPolygon);
                return nullptr;
            }
        }
    } else {
        std::cerr << "Invalid coordinates format for MultiPolygon." << std::endl;
        OGRGeometryFactory::destroyGeometry(multiPolygon);
        return nullptr;
    }

    return multiPolygon;
}

// Function to parse GeoJSON and return an OGRGeometry object
OGRGeometry* parseGeoJSON(const std::string& geojson) {
    Json::CharReaderBuilder rbuilder;
    std::string errs;
    Json::Value root;
    std::istringstream s(geojson);
    if (!Json::parseFromStream(rbuilder, s, &root, &errs)) {
        std::cerr << "Failed to parse GeoJSON: " << errs << std::endl;
        return nullptr;
    }

    std::string type = root["type"].asString();
    if (type == "Polygon") {
        return parsePolygonGeoJSON(root);
    } else if (type == "MultiPolygon") {
        return parseMultiPolygonGeoJSON(root);
    } else {
        std::cerr << "Unsupported GeoJSON geometry type: " << type << std::endl;
        return nullptr;
    }
}

// Function to get the bounding box of the geometry
void getBoundingBox(OGRGeometry* geom, double* minX, double* maxX, double* minY, double* maxY) {
    OGREnvelope envelope;
    geom->getEnvelope(&envelope);
    *minX = envelope.MinX;
    *maxX = envelope.MaxX;
    *minY = envelope.MinY;
    *maxY = envelope.MaxY;
}

// Function to calculate population inside the geometry
double calculatePopulation(OGRGeometry* geometry, const std::string& rasterFilePath) {
    if (geometry == nullptr) {
        std::cerr << "Invalid geometry." << std::endl;
        return 0.0;
    }

    GDALAllRegister();
    GDALDataset* poDataset = (GDALDataset*)GDALOpen(rasterFilePath.c_str(), GA_ReadOnly);
    if (poDataset == nullptr) {
        std::cerr << "Failed to open raster file." << std::endl;
        return 0.0;
    }

    GDALRasterBand* poBand = poDataset->GetRasterBand(1);
    int nXSize = poBand->GetXSize();
    int nYSize = poBand->GetYSize();

    double adfGeoTransform[6];
    poDataset->GetGeoTransform(adfGeoTransform);

    double minX, maxX, minY, maxY;
    getBoundingBox(geometry, &minX, &maxX, &minY, &maxY);

    int xStart = static_cast<int>((minX - adfGeoTransform[0]) / adfGeoTransform[1]);
    int xEnd = static_cast<int>((maxX - adfGeoTransform[0]) / adfGeoTransform[1]);
    int yStart = static_cast<int>((maxY - adfGeoTransform[3]) / adfGeoTransform[5]);
    int yEnd = static_cast<int>((minY - adfGeoTransform[3]) / adfGeoTransform[5]);

    xStart = std::max(0, xStart);
    xEnd = std::min(nXSize - 1, xEnd);
    yStart = std::max(0, yStart);
    yEnd = std::min(nYSize - 1, yEnd);

    double population = 0.0;
    std::vector<int> scanline(nXSize);

    // Get NoData value from the raster band
    double noDataValue = poBand->GetNoDataValue();

    for (int i = yStart; i <= yEnd; i++) {
        poBand->RasterIO(GF_Read, 0, i, nXSize, 1, scanline.data(), nXSize, 1, GDT_Int32, 0, 0);

        for (int j = xStart; j <= xEnd; j++) {
            double lon = adfGeoTransform[0] + j * adfGeoTransform[1] + i * adfGeoTransform[2];
            double lat = adfGeoTransform[3] + j * adfGeoTransform[4] + i * adfGeoTransform[5];

            OGRPoint point(lon, lat);
            if (geometry->Contains(&point)) {
                int pixelValue = scanline[j];
                // Skip NoData values
                if (pixelValue != static_cast<int>(noDataValue)) {
                    population += pixelValue;
                }
            }
        }
    }

    GDALClose((GDALDatasetH)poDataset);
    return population;
}

// Python binding
namespace py = pybind11;

double calculate_population_py(const std::string& geojson, const std::string& rasterFilePath) {
    OGRGeometry* geometry = parseGeoJSON(geojson);
    if (geometry == nullptr) {
        throw std::runtime_error("Failed to parse GeoJSON.");
    }

    double population = calculatePopulation(geometry, rasterFilePath);
    OGRGeometryFactory::destroyGeometry(geometry);
    return population;
}

PYBIND11_MODULE(population_calculator, m) {
    m.def("calculate_population", &calculate_population_py, "Calculate population inside a geometry from GeoJSON",
          py::arg("geojson"), py::arg("rasterFilePath"));
}
