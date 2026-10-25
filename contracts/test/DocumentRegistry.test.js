const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("DocumentRegistry Smart Contract", function () {
  let registry;
  let owner;
  let auditor;
  let attacker;

  const mockDocHash = ethers.keccak256(ethers.toUtf8Bytes("Physical Invoice #INV-2026-001 Bytes"));
  const mockDataHash = ethers.keccak256(ethers.toUtf8Bytes("Canonical Gemini Structured JSON Extraction"));
  const tamperedDataHash = ethers.keccak256(ethers.toUtf8Bytes("Altered Fraudulent Subtotal JSON"));

  beforeEach(async function () {
    [owner, auditor, attacker] = await ethers.getSigners();
    const DocumentRegistry = await ethers.getContractFactory("DocumentRegistry");
    registry = await DocumentRegistry.deploy();
    await registry.waitForDeployment();
  });

  it("Should notarize a document and emit DocumentNotarized event", async function () {
    const tx = await registry.notarizeDocument(
      mockDocHash,
      mockDataHash,
      "INVOICE",
      "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
    );

    await expect(tx)
      .to.emit(registry, "DocumentNotarized")
      .withArgs(
        mockDocHash,
        mockDataHash,
        owner.address,
        "INVOICE",
        "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
        await ethers.provider.getBlock("latest").then(b => b.timestamp)
      );

    expect(await registry.totalDocumentsNotarized()).to.equal(1);
  });

  it("Should verify authentic document as intact = true", async function () {
    await registry.notarizeDocument(mockDocHash, mockDataHash, "INVOICE", "ipfs://test");

    const [exists, intact, uploader, timestamp] = await registry.connect(auditor).verifyDocument(
      mockDocHash,
      mockDataHash
    );

    expect(exists).to.be.true;
    expect(intact).to.be.true;
    expect(uploader).to.equal(owner.address);
    expect(timestamp).to.be.greaterThan(0);
  });

  it("Should flag tampered JSON extraction as intact = false", async function () {
    await registry.notarizeDocument(mockDocHash, mockDataHash, "INVOICE", "ipfs://test");

    const [exists, intact, uploader, timestamp] = await registry.connect(auditor).verifyDocument(
      mockDocHash,
      tamperedDataHash // Altered data hash!
    );

    expect(exists).to.be.true;
    expect(intact).to.be.false; // Tamper detected!
    expect(uploader).to.equal(owner.address);
  });

  it("Should prevent double-claiming of the same document hash", async function () {
    await registry.notarizeDocument(mockDocHash, mockDataHash, "INVOICE", "ipfs://test");

    // Attacker attempts to register the exact same document hash
    await expect(
      registry.connect(attacker).notarizeDocument(mockDocHash, mockDataHash, "INVOICE", "ipfs://stolen")
    ).to.be.revertedWithCustomError(registry, "DocumentAlreadyRegistered");
  });

  it("Should revert on zero hash inputs", async function () {
    await expect(
      registry.notarizeDocument(ethers.ZeroHash, mockDataHash, "INVOICE", "")
    ).to.be.revertedWithCustomError(registry, "InvalidZeroHash");
  });
});
