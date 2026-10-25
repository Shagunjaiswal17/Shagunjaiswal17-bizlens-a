// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title DocumentRegistry
 * @dev BizLens AI Proof-of-Document Notarization Smart Contract
 * @notice Stores cryptographic SHA-256 fingerprints of raw documents and their
 * canonical AI-extracted JSON models on Polygon Amoy. Prevents double-claiming,
 * invoice fraud, and retroactive document tampering.
 */
contract DocumentRegistry {
    // --- Data Structures ---

    struct DocumentRecord {
        bytes32 docHash;          // SHA-256 fingerprint of original file bytes
        bytes32 dataHash;         // Canonical SHA-256 of Gemini-extracted JSON
        string docType;           // "INVOICE", "RECEIPT", "BUSINESS_CARD"
        string ipfsCid;           // IPFS CID or decentralised storage URI
        address uploader;         // Uploader wallet address
        uint256 timestamp;        // Block timestamp of notarization
        bool isRegistered;        // Guards against double-registration
    }

    // --- State Storage ---

    // Primary index: Physical Document SHA-256 -> Record
    mapping(bytes32 => DocumentRecord) private _documents;

    // Secondary index: Wallet Address -> Array of notarized document hashes
    mapping(address => bytes32[]) private _userDocuments;

    // Total counter of all on-chain registered documents
    uint256 public totalDocumentsNotarized;

    // --- Events ---

    event DocumentNotarized(
        bytes32 indexed docHash,
        bytes32 indexed dataHash,
        address indexed uploader,
        string docType,
        string ipfsCid,
        uint256 timestamp
    );

    // --- Custom Errors ---
    error DocumentAlreadyRegistered(bytes32 docHash, address existingUploader, uint256 originalTimestamp);
    error InvalidZeroHash();

    // --- External / Public Methods ---

    /**
     * @notice Notarizes a new physical document and its structured JSON extraction on-chain.
     * @param _docHash SHA-256 hash of the physical PDF/image
     * @param _dataHash Canonical SHA-256 hash of the Gemini structured JSON
     * @param _docType Classification string ("INVOICE", "RECEIPT", "BUSINESS_CARD")
     * @param _ipfsCid IPFS CID pointing to encrypted or pinned file metadata
     */
    function notarizeDocument(
        bytes32 _docHash,
        bytes32 _dataHash,
        string calldata _docType,
        string calldata _ipfsCid
    ) external {
        if (_docHash == bytes32(0) || _dataHash == bytes32(0)) {
            revert InvalidZeroHash();
        }

        // Anti-tamper & anti-double-claiming guard
        if (_documents[_docHash].isRegistered) {
            DocumentRecord memory existing = _documents[_docHash];
            revert DocumentAlreadyRegistered(_docHash, existing.uploader, existing.timestamp);
        }

        // Store immutable document record
        _documents[_docHash] = DocumentRecord({
            docHash: _docHash,
            dataHash: _dataHash,
            docType: _docType,
            ipfsCid: _ipfsCid,
            uploader: msg.sender,
            timestamp: block.timestamp,
            isRegistered: true
        });

        _userDocuments[msg.sender].push(_docHash);
        totalDocumentsNotarized++;

        emit DocumentNotarized(
            _docHash,
            _dataHash,
            msg.sender,
            _docType,
            _ipfsCid,
            block.timestamp
        );
    }

    /**
     * @notice Independent Public Verification function used by auditors, banks, or counterparties.
     * @param _docHash SHA-256 hash of physical file to verify
     * @param _dataHash SHA-256 hash of extracted JSON data
     * @return exists True if document was ever registered on Polygon Amoy
     * @return intact True if the extracted data hash matches the immutable on-chain record
     * @return uploader Wallet address of registering entity
     * @return timestamp Block timestamp when document was notarized
     */
    function verifyDocument(
        bytes32 _docHash,
        bytes32 _dataHash
    ) external view returns (
        bool exists,
        bool intact,
        address uploader,
        uint256 timestamp
    ) {
        DocumentRecord memory record = _documents[_docHash];
        if (!record.isRegistered) {
            return (false, false, address(0), 0);
        }

        exists = true;
        intact = (record.dataHash == _dataHash);
        uploader = record.uploader;
        timestamp = record.timestamp;
    }

    /**
     * @notice Retrieve complete record details by document SHA-256 hash.
     */
    function getDocument(bytes32 _docHash) external view returns (DocumentRecord memory) {
        return _documents[_docHash];
    }

    /**
     * @notice Retrieve all document hashes notarized by a specific wallet address.
     */
    function getUserDocuments(address _user) external view returns (bytes32[] memory) {
        return _userDocuments[_user];
    }
}
