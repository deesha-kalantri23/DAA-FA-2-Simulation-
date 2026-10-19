/**
 * merge_sort.cpp
 * Manual C++ implementation of Merge Sort for Flood Evacuation Priority System.
 * 
 * Course: Design and Analysis of Algorithms (DAA) FA-2
 * Strategy: Divide and Conquer
 * Sorting Order: Descending based on Water Level (Triage Priority)
 * Constraint: Zero use of std::sort() or built-in sorting libraries.
 */

#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>

struct FloodArea {
    std::string area_id;
    std::string name;
    double water_level;
    int population;

    std::string get_priority() const {
        if (water_level >= 7.5) return "CRITICAL";
        if (water_level >= 6.0) return "HIGH";
        if (water_level >= 4.0) return "MEDIUM";
        return "LOW";
    }
};

class MergeSortEngine {
private:
    int comparison_count = 0;
    int merge_count = 0;

    void merge(std::vector<FloodArea>& arr, int start, int mid, int end, int depth) {
        // Create left and right copies
        std::vector<FloodArea> left_sub;
        std::vector<FloodArea> right_sub;

        for (int i = start; i <= mid; ++i) {
            left_sub.push_back(arr[i]);
        }
        for (int j = mid + 1; j <= end; ++j) {
            right_sub.push_back(arr[j]);
        }

        std::vector<FloodArea> merged_buffer;
        size_t i = 0;
        size_t j = 0;

        // Compare and merge in DESCENDING order of water level
        while (i < left_sub.size() && j < right_sub.size()) {
            comparison_count++;
            
            // In disaster triage, higher water level = higher priority
            if (left_sub[i].water_level >= right_sub[j].water_level) {
                merged_buffer.push_back(left_sub[i]);
                i++;
            } else {
                merged_buffer.push_back(right_sub[j]);
                j++;
            }
        }

        // Collect remaining elements from left subarray
        while (i < left_sub.size()) {
            merged_buffer.push_back(left_sub[i]);
            i++;
        }

        // Collect remaining elements from right subarray
        while (j < right_sub.size()) {
            merged_buffer.push_back(right_sub[j]);
            j++;
        }

        // Copy merged buffer back into the primary array
        merge_count++;
        for (size_t k = 0; k < merged_buffer.size(); ++k) {
            arr[start + k] = merged_buffer[k];
        }
    }

    void merge_sort_recursive(std::vector<FloodArea>& arr, int start, int end, int depth) {
        if (start >= end) return;

        int mid = start + (end - start) / 2;

        // Divide Left Half
        merge_sort_recursive(arr, start, mid, depth + 1);

        // Divide Right Half
        merge_sort_recursive(arr, mid + 1, end, depth + 1);

        // Merge two sorted halves
        merge(arr, start, mid, end, depth);
    }

public:
    void sort(std::vector<FloodArea>& arr) {
        comparison_count = 0;
        merge_count = 0;
        if (!arr.empty()) {
            merge_sort_recursive(arr, 0, static_cast<int>(arr.size()) - 1, 0);
        }
    }

    int get_comparison_count() const { return comparison_count; }
    int get_merge_count() const { return merge_count; }
};

int main() {
    std::cout << "========================================================\n";
    std::cout << "FLOOD EVACUATION PRIORITY SYSTEM — C++ MERGE SORT BACKEND\n";
    std::cout << "Design and Analysis of Algorithms (DAA FA-2)\n";
    std::cout << "========================================================\n\n";

    std::ifstream file("flood_areas.csv");
    if (!file.is_open()) {
        std::cerr << "Error: Could not open flood_areas.csv\n";
        return 1;
    }

    std::vector<FloodArea> areas;
    std::string line;
    // Skip header line
    std::getline(file, line);

    while (std::getline(file, line)) {
        if (line.empty()) continue;
        std::stringstream ss(line);
        std::string id, name, level_str, pop_str;

        if (std::getline(ss, id, ',') &&
            std::getline(ss, name, ',') &&
            std::getline(ss, level_str, ',') &&
            std::getline(ss, pop_str, ',')) {
            
            FloodArea area;
            area.area_id = id;
            area.name = name;
            area.water_level = std::stod(level_str);
            area.population = std::stoi(pop_str);
            areas.push_back(area);
        }
    }
    file.close();

    std::cout << "Loaded " << areas.size() << " flood zones from flood_areas.csv.\n\n";

    MergeSortEngine engine;
    engine.sort(areas);

    std::cout << "FINAL EVACUATION PRIORITY RANKING (DESCENDING WATER LEVEL):\n";
    std::cout << "----------------------------------------------------------------------\n";
    std::cout << std::left << std::setw(6) << "RANK"
              << std::setw(6) << "ID"
              << std::setw(18) << "AREA NAME"
              << std::setw(16) << "WATER LEVEL"
              << std::setw(14) << "POPULATION"
              << "PRIORITY\n";
    std::cout << "----------------------------------------------------------------------\n";

    for (size_t i = 0; i < areas.size(); ++i) {
        std::cout << std::left << std::setw(6) << (std::string("#") + std::to_string(i + 1))
                  << std::setw(6) << areas[i].area_id
                  << std::setw(18) << areas[i].name
                  << std::setw(16) << (std::to_string(areas[i].water_level).substr(0, 3) + " m")
                  << std::setw(14) << areas[i].population
                  << areas[i].get_priority() << "\n";
    }

    std::cout << "----------------------------------------------------------------------\n";
    std::cout << "Total Comparisons Performed: " << engine.get_comparison_count() << "\n";
    std::cout << "Total Merge Operations:      " << engine.get_merge_count() << "\n";
    std::cout << "========================================================\n";

    return 0;
}
