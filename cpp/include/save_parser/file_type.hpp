#pragma once
#include <iostream>


enum class FileType : uint32_t {
    ABCA = 0xABCA,
    ABCD = 0xABCD,
    ABCE = 0xABCE,
    ABCF = 0xABCF,
};


inline std::ostream& operator<<(std::ostream& out, FileType file_type) {
    switch (file_type) {
        case FileType::ABCA:
            out << "ABCA";
            break;
        case FileType::ABCD:
            out << "ABCD";
            break;
        case FileType::ABCE:
            out << "ABCE";
            break;
        case FileType::ABCF:
            out << "ABCF";
            break;
        default:
            throw std::runtime_error("Unexpected file type.");
    }
    return out;
}
