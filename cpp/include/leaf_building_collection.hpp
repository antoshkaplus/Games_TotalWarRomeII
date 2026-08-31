#pragma once

template<typename T>
concept Indices = std::same_as<T, const std::vector<int>&>;

template<typename T>
concept LeafBuildingCollection = requires(T t) {
    { t.leafs(int()) } -> Indices;
    { t.Leafs() } -> Indices;
    { t.PortLeafs() } -> Indices;
    { t.MajorHeadLeafs() } -> Indices;
    { t.MajorOtherLeafs() } -> Indices;
    { t.MinorHeadLeafs() } -> Indices;
    { t.MinorOtherLeafs() } -> Indices;
    { t.MinorOnlyOtherLeafs() } -> Indices;
    { t.CommonOtherLeafs() } -> Indices;

    { t[int()] } -> std::same_as<const Building&>;
    { t.buildings() } -> std::same_as<const std::vector<Building>&>;
};