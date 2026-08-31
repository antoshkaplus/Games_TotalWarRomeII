#pragma once
#include <iostream>



enum class NodeType : uint8_t {
    ASCII = 0x0f,
    Binary41 = 0x41,
    Binary42 = 0x42,
    Binary43 = 0x43,
    Binary44 = 0x44,
    Binary45 = 0x45,
    Binary46 = 0x46,
    Binary47 = 0x47,
    Binary48 = 0x48,
    Binary49 = 0x49,
    Binary4A = 0x4a,
    Binary4B = 0x4b,
    Binary4C = 0x4c,
    Binary4D = 0x4d,
    Boolean = 1,
    Byte = 6,
    Float = 0X0a,
    FloatPoint = 0X0c,
    FloatPoint3D = 0x0d,
    Int = 4,
    PolyNode = 0x81, // 0b10000001???
    Short = 0,

    UInt = 8,
    UInt16 = 7,
    UShort = 0x10,
    UTF16 = 0x0e,

    // ABCA specific
    RootRecord = 0x80, // 0b10000000
    Record = 0xa0, // 0b10100000
};


//inline bool


inline std::ostream& operator<<(std::ostream& out, NodeType val_type) {
    switch (val_type) {
        case NodeType::ASCII:
            out << "ASCII";
            break;
        case NodeType::Binary41:
        case NodeType::Binary42:
        case NodeType::Binary43:
        case NodeType::Binary44:
        case NodeType::Binary45:
        case NodeType::Binary46:
        case NodeType::Binary47:
        case NodeType::Binary48:
        case NodeType::Binary49:
        case NodeType::Binary4A:
        case NodeType::Binary4B:
        case NodeType::Binary4C:
        case NodeType::Binary4D:
            out << "Binary";
            break;
        case NodeType::Boolean:
            out << "Boolean";
            break;
        case NodeType::Byte:
            out << "Byte";
            break;
        case NodeType::Float:
            out << "Float";
            break;
        case NodeType::FloatPoint:
            out << "FloatPoint";
            break;
        case NodeType::FloatPoint3D:
            out << "FloatPoint3D";
            break;
        case NodeType::Int:
            out << "Int";
            break;
        case NodeType::PolyNode:
            out << "PolyNode";
            break;
        case NodeType::Short:
            out << "Short";
            break;
        case NodeType::RootRecord:
            out << "SingleNode";
            break;
        case NodeType::UInt:
            out << "UInt";
            break;
        case NodeType::UInt16:
            out << "UInt16";
            break;
        case NodeType::UShort:
            out << "UShort";
            break;
        case NodeType::UTF16:
            out << "UTF16";
            break;
        default:
            throw std::runtime_error("Unexpected ESF_ValueType value.");
    }
    return out;
}
